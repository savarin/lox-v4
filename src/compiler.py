from typing import Dict, List, Optional, Tuple, Union
import dataclasses
import enum

import expr
import statem
import token_class
import token_type


Byte = Union["OpCode", int, None]


INT_COUNT = 16


class OpCode(enum.Enum):
    """ """

    OP_CONSTANT = "OP_CONSTANT"
    OP_POP = "OP_POP"
    OP_GET = "OP_GET"
    OP_SET = "OP_SET"
    OP_EQUAL = "OP_EQUAL"
    OP_GREATER = "OP_GREATER"
    OP_LESS = "OP_LESS"
    OP_ADD = "OP_ADD"
    OP_SUBTRACT = "OP_SUBTRACT"
    OP_MULTIPLY = "OP_MULTIPLY"
    OP_DIVIDE = "OP_DIVIDE"
    OP_NOT = "OP_NOT"
    OP_NEGATE = "OP_NEGATE"
    OP_PRINT = "OP_PRINT"
    OP_JUMP = "OP_JUMP"
    OP_JUMP_CONDITIONAL = "OP_JUMP_CONDITIONAL"


operator_mapping: Dict[token_type.TokenType, OpCode] = {
    token_type.TokenType.PLUS: OpCode.OP_ADD,
    token_type.TokenType.MINUS: OpCode.OP_SUBTRACT,
    token_type.TokenType.STAR: OpCode.OP_MULTIPLY,
    token_type.TokenType.SLASH: OpCode.OP_DIVIDE,
    token_type.TokenType.BANG_EQUAL: OpCode.OP_EQUAL,
    token_type.TokenType.EQUAL_EQUAL: OpCode.OP_EQUAL,
    token_type.TokenType.GREATER: OpCode.OP_GREATER,
    token_type.TokenType.GREATER_EQUAL: OpCode.OP_LESS,
    token_type.TokenType.LESS: OpCode.OP_LESS,
    token_type.TokenType.LESS_EQUAL: OpCode.OP_GREATER,
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


def write(vector: Values, constant: int) -> Tuple[Values, int]:
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

    elif isinstance(statement, statem.If):
        individual_bytecode, vector = evaluate(statement.condition, listing, vector)
        bytecode += individual_bytecode

        # Represents body of first emit_jump. First placeholder for location to jump to if true,
        # second placeholder if false.
        bytecode.append(OpCode.OP_JUMP_CONDITIONAL)
        bytecode.append(0xFF)
        bytecode.append(0xFF)
        then_location = len(bytecode) - 2

        # The jump instruction peeks on the stack, pop needed to remove the condition result from
        # the stack when the condition is true.
        bytecode.append(OpCode.OP_POP)

        individual_bytecode, listing, vector = execute(
            statement.then_branch, listing, vector
        )
        bytecode += individual_bytecode

        # Represents body of second emit_jump. Placeholder for location to jump to after then branch
        # execution is complete.
        bytecode.append(OpCode.OP_JUMP)
        bytecode.append(0xFF)
        else_location = len(bytecode) - 1

        # Represents body of first patch_jump. Sets the known location of the start of the then
        # branch and the start of the else branch in placeholders of first emit_jump.
        bytecode[then_location] = 2
        bytecode[then_location + 1] = len(bytecode) - then_location - 1

        # Remove the condition result from the stack when the condition is false and jump to the
        # start of the else branch takes place.
        bytecode.append(OpCode.OP_POP)

        if statement.else_branch is not None:
            individual_bytecode, listing, vector = execute(
                statement.else_branch, listing, vector
            )
            bytecode += individual_bytecode

        # Represents body of second patch_jump. Sets the known location of the end of the else
        # branch in placeholders of the second emit_jump.
        bytecode[else_location] = len(bytecode) - else_location

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

    if isinstance(expression, expr.Assign):
        individual_bytecode, vector = evaluate(expression.value, listing, vector)
        bytecode += individual_bytecode

        location = resolve_local(listing, expression.name)

        if location is not None:
            bytecode.append(OpCode.OP_SET)
            bytecode.append(location)

            return bytecode, vector

    elif isinstance(expression, expr.Binary):
        individual_bytecode, vector = evaluate(expression.left, listing, vector)
        bytecode += individual_bytecode

        individual_bytecode, vector = evaluate(expression.right, listing, vector)
        bytecode += individual_bytecode

        individual_type = expression.operator.token_type

        operator = operator_mapping[individual_type]
        bytecode.append(operator)

        if individual_type in [
            token_type.TokenType.BANG_EQUAL,
            token_type.TokenType.GREATER_EQUAL,
            token_type.TokenType.LESS_EQUAL,
        ]:
            bytecode.append(OpCode.OP_NOT)

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

    elif isinstance(expression, expr.Variable):
        location = resolve_local(listing, expression.name)

        if location is not None:
            bytecode.append(OpCode.OP_GET)
            bytecode.append(location)

            return bytecode, vector

    raise Exception


def resolve_local(
    listing: Locals, individual_token: token_class.Token
) -> Optional[int]:
    """ """
    for i in range(listing.count - 1, -1, -1):
        local = listing.array[i]
        assert local.name is not None

        if individual_token.lexeme == local.name.lexeme:
            return i

    return None
