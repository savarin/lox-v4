from typing import Dict, List, Optional, Tuple, Union
import dataclasses
import enum

import expr
import statem
import token_class
import token_type


Byte = Union["OpCode", int, None]


INT_COUNT = 8


class OpCode(enum.Enum):
    """ """

    OP_CONSTANT = "OP_CONSTANT"
    OP_POP = "OP_POP"
    OP_GET = "OP_GET"
    OP_SET = "OP_SET"
    OP_ADD = "OP_ADD"
    OP_SUBTRACT = "OP_SUBTRACT"
    OP_MULTIPLY = "OP_MULTIPLY"
    OP_DIVIDE = "OP_DIVIDE"
    OP_NEGATE = "OP_NEGATE"
    OP_PRINT = "OP_PRINT"


operator_mapping: Dict[token_type.TokenType, OpCode] = {
    token_type.TokenType.PLUS: OpCode.OP_ADD,
    token_type.TokenType.MINUS: OpCode.OP_SUBTRACT,
    token_type.TokenType.STAR: OpCode.OP_MULTIPLY,
    token_type.TokenType.SLASH: OpCode.OP_DIVIDE,
}


@dataclasses.dataclass
class Local:
    """ """

    name: Optional[token_class.Token]
    depth: int


@dataclasses.dataclass
class Locals:
    """ """

    array: List[Local]
    count: int
    scope_depth: int


def init_locals() -> Locals:
    """ """
    array = [Local(None, 0) for _ in range(INT_COUNT)]
    return Locals(array=array, count=0, scope_depth=0)


@dataclasses.dataclass
class Value:
    """ """

    value: Optional[int]


@dataclasses.dataclass
class Values:
    """ """

    array: List[Value]
    count: int


def init_values() -> Values:
    """ """
    array: List[Value] = [Value(None) for _ in range(INT_COUNT)]
    return Values(array=array, count=0)


def write(vector: Values, constant: int):
    """ """
    vector.array[vector.count] = Value(constant)
    vector.count += 1

    return vector, vector.count - 1


@dataclasses.dataclass
class Compiler:
    """ """

    statements: List[statem.Statem]


def init_compiler(statements: List[statem.Statem]) -> Compiler:
    """ """
    return Compiler(statements=statements)


def compile(composer: Compiler) -> Tuple[List[Byte], Values]:
    """ """
    bytecode: List[Byte] = []
    listing = init_locals()
    vector = init_values()

    for statement in composer.statements:
        individual_bytecode, listing, vector = execute(statement, listing, vector)
        bytecode += individual_bytecode

    return bytecode, vector


def execute(
    statement: statem.Statem, listing: Locals, vector: Values
) -> Tuple[List[Byte], Locals, Values]:
    """ """
    bytecode: List[Byte] = []

    if isinstance(statement, statem.Block):
        return execute_block(statement.statements, listing, vector)

    elif isinstance(statement, statem.Expression):
        individual_bytecode, vector = evaluate(statement.expression, listing, vector)
        bytecode += individual_bytecode
        bytecode.append(OpCode.OP_POP)

        return bytecode, listing, vector

    elif isinstance(statement, statem.Print):
        individual_bytecode, vector = evaluate(statement.expression, listing, vector)
        bytecode += individual_bytecode
        bytecode.append(OpCode.OP_PRINT)

        return bytecode, listing, vector

    elif isinstance(statement, statem.Var):
        value: List[Byte] = [OpCode.OP_CONSTANT, None]

        if statement.initializer is not None:
            value, vector = evaluate(statement.initializer, listing, vector)

        bytecode += value

        listing.array[listing.count] = Local(statement.name, listing.scope_depth)
        listing.count += 1

        return bytecode, listing, vector

    raise Exception


def execute_block(
    statements: List[statem.Statem], listing: Locals, vector: Values
) -> Tuple[List[Byte], Locals, Values]:
    """ """
    bytecode: List[Byte] = []

    # Increase scope depth when entering block.
    listing.scope_depth += 1

    for statement in statements:
        individual_bytecode, listing, vector = execute(statement, listing, vector)
        bytecode += individual_bytecode

    # Decrease scope depth when exiting block and remove out of scope variables.
    listing.scope_depth -= 1

    while True:
        local = listing.array[listing.count - 1]
        assert local is not None

        if listing.count == 0 or local.depth <= listing.scope_depth:
            break

        bytecode.append(OpCode.OP_POP)
        listing.count -= 1

    return bytecode, listing, vector


def evaluate(
    expression: expr.Expr, listing: Locals, vector: Values
) -> Tuple[List[Byte], Values]:
    """ """
    bytecode: List[Byte] = []

    # For variable assigment, similar walk as variable declaration. Difference in operation is
    # handled in the VM.
    if isinstance(expression, expr.Assign):
        individual_bytecode, vector = evaluate(expression.value, listing, vector)
        bytecode += individual_bytecode

        for i in range(listing.count - 1, -1, -1):
            local = listing.array[i]
            assert local is not None
            assert local.name is not None

            if expression.name.lexeme == local.name.lexeme:
                bytecode.append(OpCode.OP_SET)
                bytecode.append(i)

                return bytecode, vector

    if isinstance(expression, expr.Binary):
        individual_bytecode, vector = evaluate(expression.left, listing, vector)
        bytecode += individual_bytecode

        individual_bytecode, vector = evaluate(expression.right, listing, vector)
        bytecode += individual_bytecode

        operator = operator_mapping[expression.operator.token_type]
        bytecode.append(operator)

        return bytecode, vector

    elif isinstance(expression, expr.Grouping):
        individual_bytecode, vector = evaluate(expression.expression, listing, vector)
        bytecode += individual_bytecode

        return bytecode, vector

    elif isinstance(expression, expr.Literal):
        vector, location = write(vector, expression.value)
        bytecode += [OpCode.OP_CONSTANT, location]

        return bytecode, vector

    elif isinstance(expression, expr.Unary):
        individual_bytecode, vector = evaluate(expression.right, listing, vector)
        bytecode += individual_bytecode
        bytecode.append(OpCode.OP_NEGATE)

        return bytecode, vector

    # For variable declaration, walk through list of locals currently in scope and find local with
    # the same name as the identifier token. Walking the array backward to ensure last declared
    # variable with the identifier.
    elif isinstance(expression, expr.Variable):
        for i in range(listing.count - 1, -1, -1):
            local = listing.array[i]
            assert local is not None
            assert local.name is not None

            if expression.name.lexeme == local.name.lexeme:
                bytecode.append(OpCode.OP_GET)
                bytecode.append(i)

                return bytecode, vector

    raise Exception
