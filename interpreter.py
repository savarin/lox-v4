from typing import List, Optional, Tuple, Union
import dataclasses

import environment
import expr
import statem
import token_type


@dataclasses.dataclass
class Interpreter:
    """ """

    statements: List[statem.Statem]
    ecosystem: environment.Environment


def init_interpreter(statements: List[statem.Statem]) -> Interpreter:
    """ """
    ecosystem = environment.init_environment()
    return Interpreter(statements=statements, ecosystem=ecosystem)


def interpret(inspector: Interpreter) -> List[Union[int, str, None]]:
    """ """
    result: List[Union[int, str, None]] = []

    for statement in inspector.statements:
        inspector, individual_result = execute(inspector, statement)
        result += individual_result

    return result


def execute(
    inspector: Interpreter, statement: statem.Statem
) -> Tuple[Interpreter, List[Union[int, str, None]]]:
    """ """
    if isinstance(statement, statem.Block):
        ecosystem = environment.init_environment(inspector.ecosystem)
        return execute_block(inspector, statement.statements, ecosystem)

    elif isinstance(statement, statem.If):
        if is_truthy(evaluate(inspector, statement.condition)):
            return execute(inspector, statement.then_branch)

        elif statement.else_branch is not None:
            return execute(inspector, statement.else_branch)

    elif isinstance(statement, statem.Expression):
        return inspector, [evaluate(inspector, statement.expression)]

    elif isinstance(statement, statem.Print):
        return inspector, [stringify(evaluate(inspector, statement.expression))]

    elif isinstance(statement, statem.Var):
        value = None

        if statement.initializer is not None:
            value = evaluate(inspector, statement.initializer)

        inspector.ecosystem = environment.define(
            inspector.ecosystem, statement.name.lexeme, value
        )

        return inspector, [None]

    raise Exception


def execute_block(
    inspector: Interpreter,
    statements: List[statem.Statem],
    ecosystem: environment.Environment,
) -> Tuple[Interpreter, List[Union[int, str, None]]]:
    """ """
    result: List[Union[int, str, None]] = []
    previous = inspector.ecosystem

    try:
        inspector.ecosystem = ecosystem

        for statement in statements:
            inspector, individual_result = execute(inspector, statement)
            result += individual_result

    finally:
        inspector.ecosystem = previous

    return inspector, result


def evaluate(inspector: Interpreter, expression: expr.Expr) -> Union[int, bool, None]:
    """ """
    if isinstance(expression, expr.Assign):
        value = evaluate(inspector, expression.value)
        inspector.ecosystem = environment.assign(
            inspector.ecosystem, expression.name, value
        )

        return None

    elif isinstance(expression, expr.Binary):
        left = evaluate(inspector, expression.left)
        right = evaluate(inspector, expression.right)
        individual_token = expression.operator.token_type

        if individual_token == token_type.TokenType.GREATER:
            assert left is not None and right is not None
            return left > right

        elif individual_token == token_type.TokenType.GREATER_EQUAL:
            assert left is not None and right is not None
            return left >= right

        elif individual_token == token_type.TokenType.LESS:
            assert left is not None and right is not None
            return left < right

        elif individual_token == token_type.TokenType.LESS_EQUAL:
            assert left is not None and right is not None
            return left <= right

        elif individual_token == token_type.TokenType.BANG_EQUAL:
            return not is_equal(left, right)

        elif individual_token == token_type.TokenType.EQUAL_EQUAL:
            return is_equal(left, right)

        elif individual_token == token_type.TokenType.MINUS:
            assert left is not None and right is not None
            return left - right

        elif individual_token == token_type.TokenType.PLUS:
            assert left is not None and right is not None
            return left + right

        elif individual_token == token_type.TokenType.SLASH:
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
        return environment.get(inspector.ecosystem, expression.name)

    raise RuntimeError


def is_truthy(operand: Union[int, bool, None]) -> bool:
    """ """
    if operand is None:
        return False

    elif isinstance(operand, bool):
        return operand

    return True


def is_equal(a: Optional[int], b: Optional[int]) -> bool:
    """ """
    if a is None and b is None:
        return True

    elif a is None or b is None:
        return False

    return a == b


def stringify(operand: Optional[int]) -> str:
    """ """
    if operand is None:
        return "nil"

    return str(operand)
