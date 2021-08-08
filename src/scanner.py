from typing import Dict, List, Optional, Tuple
import dataclasses

import token_class
import token_type


keywords: Dict[str, token_type.TokenType] = {
    "else": token_type.TokenType.ELSE,
    "fun": token_type.TokenType.FUN,
    "if": token_type.TokenType.IF,
    "let": token_type.TokenType.LET,
    "print": token_type.TokenType.PRINT,
    "return": token_type.TokenType.RETURN,
}


@dataclasses.dataclass
class Scanner:
    """ """

    source: str
    tokens: Optional[List[token_class.Token]]
    start: int = 0
    current: int = 0
    line: int = 1


def init_scanner(source: str) -> Scanner:
    """ """
    tokens: List[token_class.Token] = []
    return Scanner(source=source, tokens=tokens)


def scan(searcher: Scanner) -> List[token_class.Token]:
    """ """
    while not is_at_end(searcher):
        searcher.start = searcher.current
        searcher = scan_token(searcher)

    assert searcher.tokens is not None
    searcher.tokens.append(
        token_class.Token(token_type.TokenType.EOF, "", None, searcher.line)
    )

    return searcher.tokens


def scan_token(searcher: Scanner) -> Scanner:
    """ """
    searcher, char = advance(searcher)

    if char == "(":
        searcher = add_token(searcher, token_type.TokenType.LEFT_PAREN)
    elif char == ")":
        searcher = add_token(searcher, token_type.TokenType.RIGHT_PAREN)
    elif char == "{":
        searcher = add_token(searcher, token_type.TokenType.LEFT_BRACE)
    elif char == "}":
        searcher = add_token(searcher, token_type.TokenType.RIGHT_BRACE)
    elif char == ",":
        searcher = add_token(searcher, token_type.TokenType.COMMA)
    elif char == "-":
        searcher = add_token(searcher, token_type.TokenType.MINUS)
    elif char == "+":
        searcher = add_token(searcher, token_type.TokenType.PLUS)
    elif char == ";":
        searcher = add_token(searcher, token_type.TokenType.SEMICOLON)
    elif char == "/":
        searcher = add_token(searcher, token_type.TokenType.SLASH)
    elif char == "*":
        searcher = add_token(searcher, token_type.TokenType.STAR)
    elif char == " ":
        pass

    elif char == "!":
        searcher = add_token(
            searcher,
            token_type.TokenType.BANG_EQUAL
            if match(searcher, "=")
            else token_type.TokenType.BANG,
        )
    elif char == "=":
        searcher = add_token(
            searcher,
            token_type.TokenType.EQUAL_EQUAL
            if match(searcher, "=")
            else token_type.TokenType.EQUAL,
        )
    elif char == ">":
        searcher = add_token(
            searcher,
            token_type.TokenType.GREATER_EQUAL
            if match(searcher, "=")
            else token_type.TokenType.GREATER,
        )
    elif char == "<":
        searcher = add_token(
            searcher,
            token_type.TokenType.LESS_EQUAL
            if match(searcher, "=")
            else token_type.TokenType.LESS,
        )

    elif char == "\n":
        searcher.line += 1

    else:
        if is_digit(char):
            searcher = number(searcher)
        elif is_alpha(char):
            searcher = identifier(searcher)

    return searcher


def identifier(searcher: Scanner) -> Scanner:
    """ """
    while is_alpha_numeric(peek(searcher)):
        searcher, _ = advance(searcher)

    text = searcher.source[searcher.start : searcher.current]
    individual_type = keywords.get(text, None)

    if individual_type is None:
        individual_type = token_type.TokenType.IDENTIFIER

    return add_token(searcher, individual_type)


def number(searcher: Scanner) -> Scanner:
    """ """
    while is_digit(peek(searcher)):
        searcher, _ = advance(searcher)

    number = int(searcher.source[searcher.start : searcher.current])
    return add_token(searcher, token_type.TokenType.NUMBER, number)


def match(searcher: Scanner, expected: str) -> bool:
    """ """
    if is_at_end(searcher):
        return False

    if searcher.source[searcher.current] != expected:
        return False

    searcher.current += 1
    return True


def peek(searcher: Scanner) -> str:
    """ """
    if is_at_end(searcher):
        return "\0"

    return searcher.source[searcher.current]


def is_alpha_numeric(char: str) -> bool:
    """ """
    return is_alpha(char) or is_digit(char)


def is_alpha(char: str) -> bool:
    """ """
    return (char >= "a" and char <= "z") or (char >= "A" and char <= "Z") or char == "_"


def is_digit(char: str) -> bool:
    """ """
    return char >= "0" and char <= "9"


def is_at_end(searcher: Scanner) -> bool:
    """ """
    return searcher.current >= len(searcher.source)


def advance(searcher: Scanner) -> Tuple[Scanner, str]:
    """ """
    char = searcher.source[searcher.current]
    searcher.current += 1

    return searcher, char


def add_token(
    searcher: Scanner,
    individual_type: token_type.TokenType,
    literal: Optional[int] = None,
) -> Scanner:
    """ """
    text = searcher.source[searcher.start : searcher.current]

    assert searcher.tokens is not None
    searcher.tokens.append(
        token_class.Token(individual_type, text, literal, searcher.line)
    )

    return searcher
