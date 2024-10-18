from lark import Transformer, v_args, Token
import narya_ast
from narya_symbol_table import SymbolTable, ScopeType
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class NaryaTransformer(Transformer):
    def __init__(self):
        super().__init__()
        self.symbol_table = SymbolTable()

    def filter_newlines(self, items):
        return [item for item in items if not (isinstance(item, Token) and item.type == 'NEWLINE')]

    @v_args(inline=True)
    def start(self, *rings):
        logger.debug(f"Start method called with {len(rings)} rings")
        return narya_ast.Program(statements=self.filter_newlines(rings))

    @v_args(inline=True)
    def ring(self, name, block):
        logger.debug(f"Ring method called with name: {name}")
        self.symbol_table.enter_scope(str(name), ScopeType.RING)
        result = narya_ast.Ring(name=str(name), body=block)
        self.symbol_table.exit_scope()
        return result

    @v_args(inline=True)
    def block(self, *statements):
        logger.debug(f"Block method called with {len(statements)} statements")
        return narya_ast.Suite(statements=self.filter_newlines(statements))

    @v_args(inline=True)
    def type_expression(self, *args):
        args = self.filter_newlines(args)
        if len(args) == 1:
            if isinstance(args[0], narya_ast.TypeExpression):
                return args[0]
            return narya_ast.TypeExpression(base_type=str(args[0]))
        elif len(args) == 2:
            if args[1] == '?':
                return narya_ast.TypeExpression(base_type=args[0].base_type, parameters=args[0].parameters, is_nullable=True, is_mutable=args[0].is_mutable)
            elif args[0] == '*':
                return narya_ast.TypeExpression(base_type=args[1].base_type, parameters=args[1].parameters, is_nullable=args[1].is_nullable, is_mutable=True)
            else:
                return narya_ast.CollectionType(base_type=str(args[0]), value_type=args[1])
        elif len(args) == 3:
            return narya_ast.CollectionType(base_type=str(args[0]), key_type=args[1], value_type=args[2])
        else:
            raise ValueError(f"Unexpected number of arguments for type_expression: {len(args)}")

    @v_args(inline=True)
    def variable_declaration(self, *args):
        logger.debug(f"Variable declaration method called with args: {args}")
        args = self.filter_newlines(args)
        is_mutable = False
        type_expr = None
        name = None
        initializer = None
        
        for arg in args:
            if isinstance(arg, str) and arg == '*':
                is_mutable = True
            elif isinstance(arg, narya_ast.TypeExpression):
                type_expr = arg
            elif isinstance(arg, str) and name is None:
                name = arg
            else:
                initializer = arg
        
        if name and type_expr:
            logger.debug(f"Adding symbol: {name} with type: {type_expr}")
            self.symbol_table.add_symbol(name, str(type_expr), "variable")
        return narya_ast.VariableDeclaration(type=type_expr, name=name, initializer=initializer, is_mutable=is_mutable)

    def collection_type(self, args):
        args = self.filter_newlines(args)
        if len(args) == 1:
            return narya_ast.TypeExpression(base_type=str(args[0]))
        else:
            return narya_ast.TypeExpression(base_type="UnknownCollectionType")

    @v_args(inline=True)
    def group_declaration(self, *args):
        args = self.filter_newlines(args)
        access_modifier = None
        name = None
        parent = None
        body = None

        for arg in args:
            if isinstance(arg, str):
                if arg in ["public", "private", "protected"]:
                    access_modifier = arg
                elif name is None:
                    name = arg
                elif parent is None:
                    parent = arg
            elif isinstance(arg, narya_ast.Suite):
                body = arg

        if name:
            self.symbol_table.add_symbol(name, "group", "group")
            self.symbol_table.enter_scope(name, ScopeType.GROUP)

        # Process the body of the group
        if body:
            for statement in body.statements:
                self.transform(statement)

        result = narya_ast.GroupDeclaration(name=name, parent=parent, body=body)
        
        if name:
            self.symbol_table.exit_scope()

        return result

    @v_args(inline=True)
    def function_declaration(self, *args):
        args = self.filter_newlines(args)
        name = None
        return_type = None
        parameters = []
        body = None

        for arg in args:
            if isinstance(arg, str) and name is None:
                name = arg
            elif isinstance(arg, narya_ast.TypeExpression) and return_type is None:
                return_type = arg
            elif isinstance(arg, list):
                parameters = arg
            elif isinstance(arg, narya_ast.Suite):
                body = arg

        if name and return_type:
            self.symbol_table.add_symbol(name, str(return_type), "function")
        self.symbol_table.enter_scope(name, ScopeType.FUNCTION)
        
        # Process function parameters
        for param in parameters:
            self.symbol_table.add_symbol(param.name, str(param.type), "parameter")

        # Process function body
        if body:
            for statement in body.statements:
                self.transform(statement)

        result = narya_ast.FunctionDeclaration(name=name, parameters=parameters, return_type=return_type, body=body)
        self.symbol_table.exit_scope()
        return result

    @v_args(inline=True)
    def do_block(self, *args):
        args = self.filter_newlines(args)
        self.symbol_table.enter_scope("do", ScopeType.CONTROL_FLOW)
        result = narya_ast.DoBlock(body=args[0])
        self.symbol_table.exit_scope()
        return result

    @v_args(inline=True)
    def if_statement(self, *args):
        args = self.filter_newlines(args)
        condition = args[0]
        if_body = args[1]
        else_body = args[2] if len(args) > 2 else None

        self.symbol_table.enter_scope("if", ScopeType.CONTROL_FLOW)
        self.transform(if_body)
        self.symbol_table.exit_scope()

        if else_body:
            self.symbol_table.enter_scope("else", ScopeType.CONTROL_FLOW)
            self.transform(else_body)
            self.symbol_table.exit_scope()

        return narya_ast.IfStatement(condition=condition, if_body=if_body, else_body=else_body)

    @v_args(inline=True)
    def while_statement(self, condition, body):
        self.symbol_table.enter_scope("while", ScopeType.CONTROL_FLOW)
        self.transform(body)
        self.symbol_table.exit_scope()
        return narya_ast.WhileStatement(condition=condition, body=body)

    @v_args(inline=True)
    def for_statement(self, variable, start, end, body):
        self.symbol_table.enter_scope("for", ScopeType.CONTROL_FLOW)
        self.symbol_table.add_symbol(variable, "int", "loop_variable")  # Assuming int type for loop variable
        self.transform(body)
        self.symbol_table.exit_scope()
        return narya_ast.ForStatement(variable=variable, start=start, end=end, body=body)

    @v_args(inline=True)
    def foreach_statement(self, variable, iterable, body):
        self.symbol_table.enter_scope("foreach", ScopeType.CONTROL_FLOW)
        self.symbol_table.add_symbol(variable, "any", "loop_variable")  # Using 'any' as we don't know the exact type
        self.transform(body)
        self.symbol_table.exit_scope()
        return narya_ast.ForeachStatement(variable=variable, iterable=iterable, body=body)

    @v_args(inline=True)
    def anonymous_scope(self, body):
        self.symbol_table.enter_scope("", ScopeType.ANONYMOUS)
        result = narya_ast.AnonymousScope(body=body)
        self.symbol_table.exit_scope()
        return result

    @v_args(inline=True)
    def dangerous_scope(self, keyword, body):
        if isinstance(body, narya_ast.AnonymousScope):
            self.symbol_table.enter_scope("", ScopeType.ANONYMOUS, is_dangerous=True)
            result = self.transform(body)
            self.symbol_table.exit_scope()
        else:
            current_scope = self.symbol_table.current_scope
            current_scope.is_dangerous = True
            result = self.transform(body)
            current_scope.is_dangerous = False
        return narya_ast.DangerousScope(body=result)

    def NEWLINE(self, token):
        logger.debug(f"NEWLINE token encountered: {token}")
        return token

    def INDENT(self, token):
        logger.debug(f"INDENT token encountered: {token}")
        return token

    def DEDENT(self, token):
        logger.debug(f"DEDENT token encountered: {token}")
        return token

    def __default__(self, data, children, meta):
        logger.debug(f"Default method called with data: {data}, children: {children}")
        if data == 'collection_type':
            return self.collection_type(children)
        filtered_children = self.filter_newlines(children)
        if not filtered_children:
            return None
        return super().__default__(data, filtered_children, meta)