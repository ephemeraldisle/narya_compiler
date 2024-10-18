from lark.indenter import Indenter

class NaryaIndenter(Indenter):
    NL_type = 'NEWLINE'
    OPEN_PAREN_types = ['LPAREN', 'LBRACKET', 'LBRACE']
    CLOSE_PAREN_types = ['RPAREN', 'RBRACKET', 'RBRACE']
    INDENT_type = 'INDENT'
    DEDENT_type = 'DEDENT'
    tab_len = 4  # Narya uses 4 spaces for indentation