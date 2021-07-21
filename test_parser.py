import expr
import parser
import scanner
import token_class
import token_type


def source_to_expression(source: str) -> expr.Expr:
    """ """
    searcher = scanner.init_scanner(source=source)
    tokens = scanner.scan_tokens(searcher)
    processor = parser.init_parser(tokens=tokens)
    parse_tuple = parser.parse(processor)

    assert parse_tuple is not None
    return parse_tuple[1]


def test_parse() -> None:
    """ """
    expression = source_to_expression(source="1 - (2 + 3)")

    assert isinstance(expression, expr.Binary)
    assert isinstance(expression.left, expr.Literal)
    assert isinstance(expression.right, expr.Grouping)
    assert expression.operator.token_type == token_type.TokenType.MINUS

    assert isinstance(expression.right.expression, expr.Binary)
    assert isinstance(expression.right.expression.left, expr.Literal)
    assert isinstance(expression.right.expression.right, expr.Literal)
    assert expression.right.expression.operator.token_type == token_type.TokenType.PLUS

    expression = source_to_expression(source="5 * (-2 - (3 + 4))")

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
