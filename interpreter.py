from typing import Optional
import dataclasses

import expr
import token_type


@dataclasses.dataclass
class Interpreter:
    """ """

    expression: expr.Expr


def init_interpreter(expression: expr.Expr) -> Interpreter:
    """ """
    return Interpreter(expression=expression)


def interpret(inspector: Interpreter) -> Optional[int]:
    """ """
    return evaluate(inspector.expression)


def evaluate(expression: expr.Expr) -> Optional[int]:
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

    elif isinstance(expression, expr.Literal):
        return expression.value

    elif isinstance(expression, expr.Unary):
        right = evaluate(expression.right)
        individual_token = expression.operator.token_type

        if individual_token == token_type.TokenType.MINUS:
            assert right is not None
            return -right

    return None
