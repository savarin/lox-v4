import enum


class TokenType(enum.Enum):
    """ """

    # Single-character tokens.
    LEFT_PAREN = "LEFT_PAREN"
    RIGHT_PAREN = "RIGHT_PAREN"
    LEFT_BRACE = "LEFT_BRACE"
    RIGHT_BRACE = "RIGHT_BRACE"
    MINUS = "MINUS"
    PLUS = "PLUS"
    SEMICOLON = "SEMICOLON"
    SLASH = "SLASH"
    STAR = "STAR"

    # One or two character tokens.
    EQUAL = "EQUAL"

    # Literals.
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"

    # Keywords
    LET = "LET"
    PRINT = "PRINT"

    EOF = "EOF"
