from typing import List, Optional, Union
import dataclasses

import environment
import expr
import statem
import token_type


@dataclasses.dataclass
class Interpreter:
    """ """

    statements: List[statem.Statem]
    enclosure: environment.Environment


def init_interpreter(statements: List[statem.Statem]) -> Interpreter:
    """ """
    enclosure = environment.init_environment()
    return Interpreter(statements=statements, enclosure=enclosure)


def interpret(inspector: Interpreter) -> List[Union[int, str, None]]:
    """ """
    result: List[Union[int, str, None]] = []

    for statement in inspector.statements:
        if isinstance(statement, statem.Expression):
            expression_result = evaluate(inspector, statement.expression) or 0
            result.append(expression_result)

        elif isinstance(statement, statem.Print):
            print_result = evaluate(inspector, statement.expression) or ""
            result.append(str(print_result))

        elif isinstance(statement, statem.Var):
            value = None

            if statement.initializer is not None:
                value = evaluate(inspector, statement.initializer)

            inspector.enclosure = environment.define(
                inspector.enclosure, statement.name.lexeme, value
            )
            result.append(None)

    return result


def evaluate(inspector: Interpreter, expression: expr.Expr) -> Optional[int]:
    """ """
    if isinstance(expression, expr.Assign):
        value = evaluate(inspector, expression.value)
        inspector.enclosure = environment.assign(
            inspector.enclosure, expression.name, value
        )
        return value

    if isinstance(expression, expr.Binary):
        left = evaluate(inspector, expression.left)
        right = evaluate(inspector, expression.right)
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
        return evaluate(inspector, expression.expression)

    elif isinstance(expression, expr.Literal):
        return expression.value

    elif isinstance(expression, expr.Unary):
        right = evaluate(inspector, expression.right)
        individual_token = expression.operator.token_type

        if individual_token == token_type.TokenType.MINUS:
            assert right is not None
            return -right

    elif isinstance(expression, expr.Variable):
        return environment.get(inspector.enclosure, expression.name)

    raise Exception
