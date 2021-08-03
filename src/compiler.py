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

    name: token_class.Token
    depth: int


@dataclasses.dataclass
class Locals:
    """ """

    array: List[Optional[Local]]
    local_count: int
    scope_depth: int


def init_locals(array: Optional[List[Optional[Local]]] = None) -> Locals:
    """ """
    if array is None:
        array = [None] * INT_COUNT

    return Locals(array=array, local_count=0, scope_depth=0)


@dataclasses.dataclass
class Compiler:
    """ """

    statements: List[statem.Statem]


def init_compiler(statements: List[statem.Statem]) -> Compiler:
    """ """
    return Compiler(statements=statements)


def compile(composer: Compiler) -> List[Byte]:
    """ """
    bytecode: List[Byte] = []
    listing = init_locals()

    for statement in composer.statements:
        individual_bytecode, listing = execute(statement, listing)
        bytecode += individual_bytecode

    return bytecode


def execute(statement: statem.Statem, listing: Locals) -> Tuple[List[Byte], Locals]:
    """ """
    bytecode: List[Byte] = []

    if isinstance(statement, statem.Block):
        return execute_block(statement.statements, listing)

    if isinstance(statement, statem.Expression):
        bytecode += evaluate(statement.expression, listing)
        bytecode.append(OpCode.OP_POP)

        return bytecode, listing

    elif isinstance(statement, statem.Print):
        bytecode += evaluate(statement.expression, listing)
        bytecode.append(OpCode.OP_PRINT)

        return bytecode, listing

    elif isinstance(statement, statem.Var):
        value: List[Byte] = [OpCode.OP_CONSTANT, None]

        if statement.initializer is not None:
            value = evaluate(statement.initializer, listing)

        bytecode += value

        listing.array[listing.local_count] = Local(statement.name, listing.scope_depth)
        listing.local_count += 1

        return bytecode, listing

    raise Exception


def execute_block(
    statements: List[statem.Statem], listing: Locals
) -> Tuple[List[Byte], Locals]:
    """ """
    bytecode: List[Byte] = []

    # Increase scope depth when entering block.
    listing.scope_depth += 1

    for statement in statements:
        individual_bytecode, listing = execute(statement, listing)
        bytecode += individual_bytecode

    # Decrease scope depth when exiting block and remove out of scope variables.
    listing.scope_depth -= 1

    while True:
        local = listing.array[listing.local_count - 1]
        assert local is not None

        if listing.local_count == 0 or local.depth <= listing.scope_depth:
            break

        bytecode.append(OpCode.OP_POP)
        listing.local_count -= 1

    return bytecode, listing


def evaluate(expression: expr.Expr, listing: Locals) -> List[Byte]:
    """ """
    bytecode: List[Byte] = []

    if isinstance(expression, expr.Binary):
        bytecode += evaluate(expression.left, listing)
        bytecode += evaluate(expression.right, listing)

        operator = operator_mapping[expression.operator.token_type]
        bytecode.append(operator)

        return bytecode

    elif isinstance(expression, expr.Grouping):
        return evaluate(expression.expression, listing)

    elif isinstance(expression, expr.Literal):
        return [OpCode.OP_CONSTANT, expression.value]

    elif isinstance(expression, expr.Unary):
        bytecode += evaluate(expression.right, listing)
        bytecode.append(OpCode.OP_NEGATE)

        return bytecode

    elif isinstance(expression, expr.Variable):
        for i in range(listing.local_count - 1, -1, -1):
            local = listing.array[i]
            assert local is not None

            if expression.name.lexeme == local.name.lexeme:
                bytecode.append(OpCode.OP_GET)
                bytecode.append(i)

                return bytecode

    raise Exception
