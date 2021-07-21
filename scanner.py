from typing import List, Optional, Tuple
import dataclasses

import token_class
import token_type


@dataclasses.dataclass
class Scanner:
    """ """

    source: str
    tokens: Optional[List[token_class.Token]] = None
    start: int = 0
    current: int = 0


def init_scanner(source: str) -> Scanner:
    """ """
    return Scanner(source=source, tokens=[])


def scan(searcher: Scanner) -> List[token_class.Token]:
    """ """
    while not is_at_end(searcher):
        searcher.start = searcher.current
        scan_token(searcher)

    assert searcher.tokens is not None
    searcher.tokens.append(token_class.Token(token_type.TokenType.EOF, "", None))

    return searcher.tokens


def scan_token(searcher: Scanner) -> Scanner:
    """ """
    searcher, char = advance(searcher)

    if char == "(":
        searcher = add_token(searcher, token_type.TokenType.LEFT_PAREN)
    elif char == ")":
        searcher = add_token(searcher, token_type.TokenType.RIGHT_PAREN)
    elif char == "-":
        searcher = add_token(searcher, token_type.TokenType.MINUS)
    elif char == "+":
        searcher = add_token(searcher, token_type.TokenType.PLUS)
    elif char == "*":
        searcher = add_token(searcher, token_type.TokenType.STAR)
    elif char == "/":
        searcher = add_token(searcher, token_type.TokenType.SLASH)
    elif char == " ":
        pass
    else:
        if is_digit(char):
            searcher = number(searcher)

    return searcher


def number(searcher: Scanner) -> Scanner:
    """ """
    while is_digit(peek(searcher)):
        searcher, _ = advance(searcher)

    number = int(searcher.source[searcher.start : searcher.current])
    return add_token(searcher, token_type.TokenType.NUMBER, number)


def peek(searcher: Scanner) -> str:
    """ """
    if is_at_end(searcher):
        return "\0"

    return searcher.source[searcher.current]


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
    searcher.tokens.append(token_class.Token(individual_type, text, literal))

    return searcher
