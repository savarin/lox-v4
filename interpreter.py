from typing import List, Tuple
import dataclasses

import expr
import statem
import token_type


@dataclasses.dataclass
class Interpreter:
    """ """

    statements: List[statem.Statem]


def init_interpreter(statements: List[statem.Statem]) -> Interpreter:
    """ """
    return Interpreter(statements=statements)


def interpret(inspector: Interpreter) -> Tuple[List[int], List[str]]:
    """ """
    expression_results: List[int] = []
    print_results: List[str] = []

    for statement in inspector.statements:
        if isinstance(statement, statem.Expression):
            expression_results.append(evaluate(statement.expression))

        elif isinstance(statement, statem.Print):
            print_result = str(evaluate(statement.expression))
            print_results.append(print_result)

    return expression_results, print_results


def evaluate(expression: expr.Expr) -> int:
    """ """
    if isinstance(expression, expr.Binary):
        left = evaluate(expression.left)
        right = evaluate(expression.right)
        individual_token = expression.operator.token_type

        if individual_token == token_type.TokenType.MINUS:
            assert left is not None and right is not None
            return left - right

        elif individual_token == token_type.TokenType.PLUS:
            assert left is not None and right is not None
            return left + right

        if individual_token == token_type.TokenType.SLASH:
            assert left is not None and right is not None
            return left // right

        elif individual_token == token_type.TokenType.STAR:
            assert left is not None and right is not None
            return left * right

    elif isinstance(expression, expr.Grouping):
        return evaluate(expression.expression)

    elif isinstance(expression, expr.Unary):
        right = evaluate(expression.right)
        individual_token = expression.operator.token_type

        if individual_token == token_type.TokenType.MINUS:
            assert right is not None
            return -right

    assert isinstance(expression, expr.Literal)
    return expression.value
