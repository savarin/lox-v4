import pytest

import expr
import parser
import scanner
import statem
import token_type


def source_to_statement(source: str) -> statem.Statem:
    """ """
    searcher = scanner.init_scanner(source=source)
    tokens = scanner.scan(searcher)
    processor = parser.init_parser(tokens=tokens)
    return parser.parse(processor)[0]


def test_valid_parse() -> None:
    """ """
    statement = source_to_statement(source="1 - (2 + 3);")
    assert isinstance(statement, statem.Expression)
    expression = statement.expression

    assert isinstance(expression, expr.Binary)
    assert isinstance(expression.left, expr.Literal)
    assert isinstance(expression.right, expr.Grouping)
    assert expression.operator.token_type == token_type.TokenType.MINUS

    assert isinstance(expression.right.expression, expr.Binary)
    assert isinstance(expression.right.expression.left, expr.Literal)
    assert isinstance(expression.right.expression.right, expr.Literal)
    assert expression.right.expression.operator.token_type == token_type.TokenType.PLUS

    statement = source_to_statement(source="5 * (-2 - (3 + 4));")
    assert isinstance(statement, statem.Expression)
    expression = statement.expression

    assert isinstance(expression, expr.Binary)
    assert isinstance(expression.left, expr.Literal)
    assert isinstance(expression.right, expr.Grouping)
    assert expression.operator.token_type == token_type.TokenType.STAR

    assert isinstance(expression.right.expression, expr.Binary)
    assert isinstance(expression.right.expression.left, expr.Unary)
    assert isinstance(expression.right.expression.right, expr.Grouping)
    assert (
        expression.right.expression.left.operator.token_type
        == token_type.TokenType.MINUS
    )

    assert isinstance(expression.right.expression.right.expression, expr.Binary)
    assert isinstance(expression.right.expression.right.expression.left, expr.Literal)
    assert isinstance(expression.right.expression.right.expression.left, expr.Literal)
    assert (
        expression.right.expression.right.expression.operator.token_type
        == token_type.TokenType.PLUS
    )


def test_invalid_parse() -> None:
    """ """
    with pytest.raises(parser.ParseError):
        source_to_statement(source="1 +;")
