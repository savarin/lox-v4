import enum


class TokenType(enum.Enum):
    """ """

    # Single-character tokens.
    LEFT_PAREN = "LEFT_PAREN"
    RIGHT_PAREN = "RIGHT_PAREN"
    MINUS = "MINUS"
    PLUS = "PLUS"
    SEMICOLON = "SEMICOLON"
    SLASH = "SLASH"
    STAR = "STAR"

    # Literals.
    NUMBER = "NUMBER"

    # Keywords
    PRINT = "PRINT"

    EOF = "EOF"
