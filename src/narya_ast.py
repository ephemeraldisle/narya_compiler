from lark.ast_utils import Ast, WithMeta, AsList
from typing import Optional, List

class TypeExpression(Ast):
    base_type: str
    parameters: Optional[List['TypeExpression']] = None
    is_nullable: bool = False
    is_mutable: bool = False

    def __init__(self, base_type, parameters=None, is_nullable=False, is_mutable=False):
        self.base_type = base_type
        self.parameters = parameters
        self.is_nullable = is_nullable
        self.is_mutable = is_mutable

class CollectionType(TypeExpression):
    value_type: 'TypeExpression'
    key_type: Optional['TypeExpression'] = None

    def __init__(self, base_type, value_type, key_type=None):
        super().__init__(base_type)
        self.value_type = value_type
        self.key_type = key_type

class VariableDeclaration(Ast):
    type: TypeExpression
    name: str
    initializer: Optional['Expression']
    is_mutable: bool

    def __init__(self, type, name, initializer=None, is_mutable=False):
        self.type = type
        self.name = name
        self.initializer = initializer
        self.is_mutable = is_mutable

class Expression(Ast):
    pass

# Add other necessary classes here...

class Program(Ast):
    statements: List[Ast]

class Ring(Ast):
    name: str
    body: 'Suite'
        
    def __init__(self, name: str, body: 'Suite'):
        self.name = name
        self.body = body

class DoBlock(Ast):
    body: 'Suite'

class Suite(Ast, AsList):
    statements: List[Ast]

    def __init__(self, statements: List[Ast]):
        self.statements = statements


class PrintStatement(Ast):
    expression: Expression

class Variable(Ast):
    name: str

class String(Ast):
    value: str

class InterpolatedString(Ast):
    parts: List[Ast]

class StringInterpolation(Ast):
    identifier: str

class Boolean(Ast):
    value: bool

class Integer(Ast):
    value: int

class Float(Ast):
    value: float

class BinaryOperation(Ast):
    left: Expression
    operator: str
    right: Expression

class FunctionCall(Ast):
    function: Expression
    arguments: List[Ast]

class FunctionDeclaration(Ast):
    name: str
    parameters: List[Ast]
    return_type: Optional[TypeExpression]
    body: 'Suite'
    
    def __init__(self, name: str, parameters: List[Ast], return_type: Optional[TypeExpression], body: 'Suite'):
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        self.body = body

class GroupDeclaration(Ast):
    name: str
    parent: Optional[str]
    body: 'Suite'
    
    def __init__(self, name: str, parent: Optional[str], body: 'Suite'):
        self.name = name
        self.parent = parent
        self.body = body

class IfStatement(Ast):
    condition: Expression
    if_body: 'Suite'
    else_body: Optional['Suite']

    def __init__(self, condition: Expression, if_body: 'Suite', else_body: Optional['Suite'] = None):
        self.condition = condition
        self.if_body = if_body
        self.else_body = else_body

class WhileStatement(Ast):
    condition: Expression
    body: 'Suite'

    def __init__(self, condition: Expression, body: 'Suite'):
        self.condition = condition
        self.body = body

class ForStatement(Ast):
    variable: str
    start: Expression
    end: Expression
    body: 'Suite'

    def __init__(self, variable: str, start: Expression, end: Expression, body: 'Suite'):
        self.variable = variable
        self.start = start
        self.end = end
        self.body = body

class ForeachStatement(Ast):
    variable: str
    iterable: Expression
    body: 'Suite'

    def __init__(self, variable: str, iterable: Expression, body: 'Suite'):
        self.variable = variable
        self.iterable = iterable
        self.body = body

class AnonymousScope(Ast):
    body: 'Suite'

    def __init__(self, body: 'Suite'):
        self.body = body

class DangerousScope(Ast):
    body: Ast

    def __init__(self, body: Ast):
        self.body = body