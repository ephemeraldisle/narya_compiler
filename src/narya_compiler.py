import os
import sys
from lark import Lark
from narya_transformer import NaryaTransformer
from narya_ast_visualizer import NaryaASTVisualizer

class NaryaCompiler:
    def __init__(self):
        self.parser = self.create_parser()
        self.transformer = NaryaTransformer()

    def create_parser(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        grammar_path = os.path.join(script_dir, "narya_grammar.lark")
        with open(grammar_path, "r") as grammar_file:
            narya_grammar = grammar_file.read()
        return Lark(narya_grammar, start="start", parser="earley")

    def compile(self, code):
        preprocessed_code = self.preprocess(code)
        parse_tree = self.parser.parse(preprocessed_code)
        ast = self.transformer.transform(parse_tree)
        return ast

    def preprocess(self, code):
        preprocessor = IndentationPreprocessor(code)
        return preprocessor.process()

    def visualize_ast(self, ast):
        visualizer = NaryaASTVisualizer()
        visualizer.visualize(ast)

class IndentationPreprocessor:
    def __init__(self, text):
        self.lines = text.splitlines()
        self.indent_stack = [0]
        self.processed_lines = []

    def process(self):
        for line_num, line in enumerate(self.lines):
            stripped = line.rstrip()
            
            if stripped:  # Non-empty line
                indent = len(line) - len(line.lstrip())
                
                if indent > self.indent_stack[-1]:
                    self.processed_lines.append("INDENT")
                    self.indent_stack.append(indent)
                elif indent < self.indent_stack[-1]:
                    while indent < self.indent_stack[-1]:
                        self.processed_lines.append("DEDENT")
                        self.indent_stack.pop()
                    if indent != self.indent_stack[-1]:
                        raise ValueError(f"Inconsistent indentation at line {line_num + 1}: {line}")
                
                self.processed_lines.append(stripped)
                self.processed_lines.append("NEWLINE")
            else:  # Empty line
                self.processed_lines.append("NEWLINE")

        # Add remaining DEDENTs
        while len(self.indent_stack) > 1:
            self.processed_lines.append("DEDENT")
            self.indent_stack.pop()

        result = " ".join(self.processed_lines)
        print("Final preprocessed code:")
        print(result)
        return result
    
if __name__ == "__main__":
    compiler = NaryaCompiler()
    
    # Sample Narya code
    narya_code = """
ring Main
    group Person
        num Age
        text Name

        public Person(num age, text name)
            Age = age
            Name = name

        public text Greeting
            return 'Hi, my name is .Name and I am .Age years old!'

    Person Charlie
        public Age = 2
        public text Greeting
            return "oi i'm charlie and i'm 30 years old, g'day mate"

    do
        *List(Person) people = Person(27, "Cassie"), Person(25, "Mimo")
        people.Add(Person(18, "Samara"), new Charlie, new Charlie())
        foreach person in people
            print person.Age
            print person.Greeting
    """

    try:
        ast = compiler.compile(narya_code)
        print("Compilation successful!")
        print("\nSymbol Table:")
        compiler.transformer.symbol_table.print_table()
        
        compiler.visualize_ast(ast)
        print("AST visualization generated: narya_ast_visualization.png")
    except Exception as e:
        print(f"Compilation error: {e}")
        import traceback
        traceback.print_exc()