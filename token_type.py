import enum


class TokenType(enum.Enum):
    """ """

    # Single-character tokens.
    LEFT_PAREN = "LEFT_PAREN"
    RIGHT_PAREN = "RIGHT_PAREN"
    MINUS = "MINUS"
    PLUS = "PLUS"
    SLASH = "SLASH"
    STAR = "STAR"

    # Literals.
    NUMBER = "NUMBER"

    EOF = "EOF"
