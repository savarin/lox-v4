from typing import List

import scanner
import token_class
import token_type


def source_to_tokens(source: str) -> List[token_class.Token]:
    """ """
    searcher = scanner.init_scanner(source=source)
    return scanner.scan(searcher)


def test_scan() -> None:
    """ """
    tokens = source_to_tokens(source="1 - (2 + 3)")

    assert tokens[0] == token_class.Token(
        token_type=token_type.TokenType.NUMBER, lexeme="1", literal=1, line=1
    )
    assert tokens[1] == token_class.Token(
        token_type=token_type.TokenType.MINUS, lexeme="-", literal=None, line=1
    )
    assert tokens[2] == token_class.Token(
        token_type=token_type.TokenType.LEFT_PAREN, lexeme="(", literal=None, line=1
    )
    assert tokens[3] == token_class.Token(
        token_type=token_type.TokenType.NUMBER, lexeme="2", literal=2, line=1
    )
    assert tokens[4] == token_class.Token(
        token_type=token_type.TokenType.PLUS, lexeme="+", literal=None, line=1
    )
    assert tokens[5] == token_class.Token(
        token_type=token_type.TokenType.NUMBER, lexeme="3", literal=3, line=1
    )
    assert tokens[6] == token_class.Token(
        token_type=token_type.TokenType.RIGHT_PAREN, lexeme=")", literal=None, line=1
    )

    tokens = source_to_tokens(source="5 * (-2 - (3 + 4))")

    assert tokens[0] == token_class.Token(
        token_type=token_type.TokenType.NUMBER, lexeme="5", literal=5, line=1
    )
    assert tokens[1] == token_class.Token(
        token_type=token_type.TokenType.STAR, lexeme="*", literal=None, line=1
    )
    assert tokens[2] == token_class.Token(
        token_type=token_type.TokenType.LEFT_PAREN, lexeme="(", literal=None, line=1
    )
    assert tokens[3] == token_class.Token(
        token_type=token_type.TokenType.MINUS, lexeme="-", literal=None, line=1
    )
    assert tokens[4] == token_class.Token(
        token_type=token_type.TokenType.NUMBER, lexeme="2", literal=2, line=1
    )
    assert tokens[5] == token_class.Token(
        token_type=token_type.TokenType.MINUS, lexeme="-", literal=None, line=1
    )
    assert tokens[6] == token_class.Token(
        token_type=token_type.TokenType.LEFT_PAREN, lexeme="(", literal=None, line=1
    )
    assert tokens[7] == token_class.Token(
        token_type=token_type.TokenType.NUMBER, lexeme="3", literal=3, line=1
    )
    assert tokens[8] == token_class.Token(
        token_type=token_type.TokenType.PLUS, lexeme="+", literal=None, line=1
    )
    assert tokens[9] == token_class.Token(
        token_type=token_type.TokenType.NUMBER, lexeme="4", literal=4, line=1
    )
    assert tokens[10] == token_class.Token(
        token_type=token_type.TokenType.RIGHT_PAREN, lexeme=")", literal=None, line=1
    )
    assert tokens[11] == token_class.Token(
        token_type=token_type.TokenType.RIGHT_PAREN, lexeme=")", literal=None, line=1
    )
