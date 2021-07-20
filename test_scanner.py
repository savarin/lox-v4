import scanner
import token_class
import token_type


def test_scan() -> None:
    """ """
    searcher = scanner.init_scanner(source="1 - (2 + 3)")
    tokens = scanner.scan_tokens(searcher)

    assert tokens[0] == token_class.Token(
        token_type=token_type.TokenType.NUMBER, lexeme="1", literal=1
    )
    assert tokens[1] == token_class.Token(
        token_type=token_type.TokenType.MINUS, lexeme="-", literal=None
    )
    assert tokens[2] == token_class.Token(
        token_type=token_type.TokenType.LEFT_PAREN, lexeme="(", literal=None
    )
    assert tokens[3] == token_class.Token(
        token_type=token_type.TokenType.NUMBER, lexeme="2", literal=2
    )
    assert tokens[4] == token_class.Token(
        token_type=token_type.TokenType.PLUS, lexeme="+", literal=None
    )
    assert tokens[5] == token_class.Token(
        token_type=token_type.TokenType.NUMBER, lexeme="3", literal=3
    )
    assert tokens[6] == token_class.Token(
        token_type=token_type.TokenType.RIGHT_PAREN, lexeme=")", literal=None
    )
