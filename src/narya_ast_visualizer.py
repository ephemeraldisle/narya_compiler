import graphviz
from narya_ast import *
from lark import Tree, Token

class NaryaASTVisualizer:
    def __init__(self):
        self.dot = graphviz.Digraph(comment='Narya AST', format='png')
        self.dot.attr(rankdir='TB', size='12,20', dpi='900', bgcolor='black')
        self.dot.attr('node', shape='box', style='filled', color='white', fontcolor='black', fontname='Courier')
        self.dot.attr('edge', color='white')
        self.counter = 0

    def add_node(self, label, color='lightblue'):
        node_id = f'node_{self.counter}'
        self.counter += 1
        self.dot.node(node_id, label, fillcolor=color)
        return node_id

    def visit(self, node, parent_id=None):
        if isinstance(node, Tree):
            return self.visit_Tree(node, parent_id)
        elif isinstance(node, Token):
            return self.visit_Token(node, parent_id)
        else:
            method_name = f'visit_{type(node).__name__}'
            method = getattr(self, method_name, self.generic_visit)
            return method(node, parent_id)

    def visit_Tree(self, node, parent_id):
        node_id = self.add_node(node.data.capitalize())
        if parent_id:
            self.dot.edge(parent_id, node_id)
        for child in node.children:
            self.visit(child, node_id)
        return node_id

    def visit_Token(self, node, parent_id):
        node_id = self.add_node(f"{node.type}\\n{node.value}", color='lightyellow')
        if parent_id:
            self.dot.edge(parent_id, node_id)
        return node_id

    def visit_Ring(self, node, parent_id):
        node_id = self.add_node(f"Ring\\n{node.name}", color='lightgreen')
        if parent_id:
            self.dot.edge(parent_id, node_id)
        self.visit(node.body, node_id)
        return node_id

    def visit_GroupDeclaration(self, node, parent_id):
        node_id = self.add_node(f"Group\\n{node.name}", color='lightpink')
        if parent_id:
            self.dot.edge(parent_id, node_id)
        self.visit(node.body, node_id)
        return node_id

    def visit_FunctionDeclaration(self, node, parent_id):
        node_id = self.add_node(f"Function\\n{node.name}", color='lightsalmon')
        if parent_id:
            self.dot.edge(parent_id, node_id)
        for param in node.parameters:
            self.visit(param, node_id)
        self.visit(node.body, node_id)
        return node_id

    def visit_VariableDeclaration(self, node, parent_id):
        node_id = self.add_node(f"Variable\\n{node.name}\\n{node.type.base_type}", color='lightcyan')
        if parent_id:
            self.dot.edge(parent_id, node_id)
        if node.initializer:
            self.visit(node.initializer, node_id)
        return node_id

    def visit_Suite(self, node, parent_id):
        for statement in node.statements:
            self.visit(statement, parent_id)
        return parent_id

    def generic_visit(self, node, parent_id):
        node_id = self.add_node(type(node).__name__)
        if parent_id:
            self.dot.edge(parent_id, node_id)
        if isinstance(node, Tree):
            for child in node.children:
                self.visit(child, node_id)
        elif hasattr(node, '__dict__'):
            for field, value in vars(node).items():
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, (Ast, Tree, Token)):
                            self.visit(item, node_id)
                elif isinstance(value, (Ast, Tree, Token)):
                    self.visit(value, node_id)
        return node_id

    def visualize(self, ast, output_file='narya_ast_visualization'):
        start_id = self.add_node('Program')
        self.visit(ast, start_id)
        self.dot.render(output_file, view=True)

# Usage example
if __name__ == "__main__":
    from narya_compiler import parser, ast_transformer, narya_code
    
    parse_tree = parser.parse(narya_code)
    ast = ast_transformer.transform(parse_tree)
    
    visualizer = NaryaASTVisualizer()
    visualizer.visualize(ast)