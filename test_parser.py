from typing import List

import pytest

import expr
import parser
import scanner
import statem
import token_type


def source_to_statements(source: str) -> List[statem.Statem]:
    """ """
    searcher = scanner.init_scanner(source=source)
    tokens = scanner.scan(searcher)
    processor = parser.init_parser(tokens=tokens)
    return parser.parse(processor)


def test_valid_expression() -> None:
    """ """
    statement = source_to_statements(source="1 - (2 + 3);")[0]
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

    statement = source_to_statements(source="5 * (-2 - (3 + 4));")[0]
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


def test_invalid_expression() -> None:
    """ """
    with pytest.raises(parser.ParseError):
        source_to_statements(source="1 +;")


def test_valid_assignment() -> None:
    """ """
    statements = source_to_statements(source="let a; print a;")

    var_declaration = statements[0]
    assert isinstance(var_declaration, statem.Var)
    assert var_declaration.name.token_type == token_type.TokenType.IDENTIFIER
    assert var_declaration.name.lexeme == "a"
    assert var_declaration.name.literal is None
    assert var_declaration.initializer is None

    print_statement = statements[1]
    assert isinstance(print_statement, statem.Print)
    assert isinstance(print_statement.expression, expr.Variable)
    assert print_statement.expression.name.token_type == token_type.TokenType.IDENTIFIER
    assert print_statement.expression.name.lexeme == "a"
    assert print_statement.expression.name.literal is None

    statements = source_to_statements(source="let a = 1; print a;")

    var_declaration = statements[0]
    assert isinstance(var_declaration, statem.Var)
    assert var_declaration.name.token_type == token_type.TokenType.IDENTIFIER
    assert var_declaration.name.lexeme == "a"
    assert var_declaration.name.literal is None
    assert isinstance(var_declaration.initializer, expr.Literal)
    assert var_declaration.initializer.value == 1

    print_statement = statements[1]
    assert isinstance(print_statement, statem.Print)
    assert isinstance(print_statement.expression, expr.Variable)
    assert print_statement.expression.name.token_type == token_type.TokenType.IDENTIFIER
    assert print_statement.expression.name.lexeme == "a"
    assert print_statement.expression.name.literal is None

    statements = source_to_statements(source="let a = 1; a = 2; print a + 3;")

    var_declaration = statements[0]
    assert isinstance(var_declaration, statem.Var)
    assert var_declaration.name.token_type == token_type.TokenType.IDENTIFIER
    assert var_declaration.name.lexeme == "a"
    assert var_declaration.name.literal is None
    assert isinstance(var_declaration.initializer, expr.Literal)
    assert var_declaration.initializer.value == 1

    assignment = statements[1]
    assert isinstance(assignment, statem.Expression)
    assert isinstance(assignment.expression, expr.Assign)
    assert assignment.expression.name.token_type == token_type.TokenType.IDENTIFIER
    assert assignment.expression.name.lexeme == "a"
    assert assignment.expression.name.literal is None
    assert isinstance(assignment.expression.value, expr.Literal)
    assert assignment.expression.value.value == 2

    print_statement = statements[2]
    assert isinstance(print_statement, statem.Print)
    assert isinstance(print_statement.expression, expr.Binary)
    assert isinstance(print_statement.expression.left, expr.Variable)
    assert (
        print_statement.expression.left.name.token_type
        == token_type.TokenType.IDENTIFIER
    )
    assert print_statement.expression.left.name.lexeme == "a"
    assert print_statement.expression.left.name.literal is None
    assert print_statement.expression.operator.token_type == token_type.TokenType.PLUS
    assert isinstance(print_statement.expression.right, expr.Literal)
    assert print_statement.expression.right.value == 3
