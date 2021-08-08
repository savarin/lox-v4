from typing import List, Optional, Tuple, Union
import dataclasses

import environment
import expr
import helpers
import statem
import token_type


@dataclasses.dataclass
class Return(Exception):
    """ """

    value: Union[helpers.Result, List[helpers.Result], statem.Function]


@dataclasses.dataclass
class Interpreter:
    """ """

    statements: List[statem.Statem]
    ecosystem: Optional[environment.Environment]


def init_interpreter(
    statements: List[statem.Statem], ecosystem: Optional[environment.Environment] = None
) -> Interpreter:
    """ """
    if ecosystem is None:
        ecosystem = environment.init_environment()

    return Interpreter(statements=statements, ecosystem=ecosystem)


def interpret(inspector: Interpreter) -> List[helpers.Result]:
    """ """
    result: List[helpers.Result] = []

    for statement in inspector.statements:
        inspector, individual_result = execute(inspector, statement)
        result += individual_result

    return result


def execute(
    inspector: Interpreter, statement: statem.Statem
) -> Tuple[Interpreter, List[helpers.Result]]:
    """ """
    assert inspector.ecosystem is not None

    if isinstance(statement, statem.Block):
        ecosystem = environment.init_environment(inspector.ecosystem)
        return execute_block(inspector, statement.statements, ecosystem)

    elif isinstance(statement, statem.Function):
        assert statement.name.lexeme is not None
        inspector.ecosystem = environment.define(
            inspector.ecosystem, statement.name.lexeme, statement
        )
        return inspector, [None]

    elif isinstance(statement, statem.Expression):
        result = evaluate(inspector, statement.expression)

        if isinstance(result, list):
            return inspector, result

        assert not isinstance(result, statem.Function)
        return inspector, [result]

    elif isinstance(statement, statem.If):
        result = evaluate(inspector, statement.condition)
        assert isinstance(result, bool)

        if helpers.is_truthy(result):
            return execute(inspector, statement.then_branch)

        elif statement.else_branch is not None:
            return execute(inspector, statement.else_branch)

        return inspector, [None]

    elif isinstance(statement, statem.Print):
        result = evaluate(inspector, statement.expression)
        assert result is None or isinstance(result, int)

        return inspector, [helpers.stringify(result)]

    elif isinstance(statement, statem.Return):
        value = None

        if statement.value is not None:
            value = evaluate(inspector, statement.value)

        raise Return(value)

    elif isinstance(statement, statem.Var):
        value = None

        if statement.initializer is not None:
            value = evaluate(inspector, statement.initializer)

        assert (
            isinstance(value, int)
            or isinstance(value, statem.Function)
            or value is None
        )
        assert statement.name.lexeme is not None
        inspector.ecosystem = environment.define(
            inspector.ecosystem, statement.name.lexeme, value
        )

        return inspector, [None]

    raise Exception


def execute_block(
    inspector: Interpreter,
    statements: List[statem.Statem],
    ecosystem: environment.Environment,
) -> Tuple[Interpreter, List[helpers.Result]]:
    """ """
    result: List[helpers.Result] = []
    previous = inspector.ecosystem

    try:
        inspector.ecosystem = ecosystem

        for statement in statements:
            result_tuple = execute(inspector, statement)

            if result_tuple is None:
                continue

            inspector, individual_result = result_tuple
            result += individual_result

    finally:
        inspector.ecosystem = previous

    return inspector, result


def evaluate(
    inspector: Interpreter, expression: expr.Expr
) -> Union[helpers.Result, List[helpers.Result], statem.Function]:
    """ """
    assert inspector.ecosystem is not None

    if isinstance(expression, expr.Assign):
        value = evaluate(inspector, expression.value)

        assert isinstance(value, int) or isinstance(value, statem.Function)
        inspector.ecosystem = environment.assign(
            inspector.ecosystem, expression.name, value
        )

        return None

    elif isinstance(expression, expr.Binary):
        left = evaluate(inspector, expression.left)
        right = evaluate(inspector, expression.right)
        individual_token = expression.operator.token_type

        assert left is None or isinstance(left, int)
        assert right is None or isinstance(right, int)

        if individual_token == token_type.TokenType.BANG_EQUAL:
            return not helpers.is_equal(left, right)

        elif individual_token == token_type.TokenType.EQUAL_EQUAL:
            return helpers.is_equal(left, right)

        assert isinstance(left, int) and isinstance(right, int)

        if individual_token == token_type.TokenType.GREATER:
            return left > right

        elif individual_token == token_type.TokenType.GREATER_EQUAL:
            return left >= right

        elif individual_token == token_type.TokenType.LESS:
            return left < right

        elif individual_token == token_type.TokenType.LESS_EQUAL:
            return left <= right

        elif individual_token == token_type.TokenType.MINUS:
            return left - right

        elif individual_token == token_type.TokenType.PLUS:
            return left + right

        elif individual_token == token_type.TokenType.SLASH:
            return left // right

        elif individual_token == token_type.TokenType.STAR:
            return left * right

    elif isinstance(expression, expr.Call):
        arguments: List[int] = []
        callee = evaluate(inspector, expression.callee)
        assert isinstance(callee, statem.Function)

        for argument in expression.arguments:
            individual_argument = evaluate(inspector, argument)
            assert isinstance(individual_argument, int)

            arguments.append(individual_argument)

        return call(inspector, callee, arguments)

    elif isinstance(expression, expr.Grouping):
        return evaluate(inspector, expression.expression)

    elif isinstance(expression, expr.Literal):
        return expression.value

    elif isinstance(expression, expr.Unary):
        right = evaluate(inspector, expression.right)
        individual_token = expression.operator.token_type

        if individual_token == token_type.TokenType.MINUS:
            assert isinstance(right, int)
            return -right

    elif isinstance(expression, expr.Variable):
        return environment.get(inspector.ecosystem, expression.name)

    raise RuntimeError


def call(
    inspector: Interpreter, function: statem.Function, arguments: List[int]
) -> Union[helpers.Result, List[helpers.Result], statem.Function]:
    """ """
    ecosystem = environment.init_environment(inspector.ecosystem)

    for i, parameter in enumerate(function.parameters):
        assert parameter.lexeme
        ecosystem = environment.define(ecosystem, parameter.lexeme, arguments[i])

    try:
        _, result = execute_block(inspector, function.body, ecosystem)
    except Return as return_value:
        return return_value.value

    return result
