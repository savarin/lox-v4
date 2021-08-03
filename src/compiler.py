from typing import Dict, List, Optional, Tuple, Union
import dataclasses
import enum

import expr
import statem
import token_class
import token_type


ByteCode = Union["OpCode", int]


INT_COUNT = 8


class OpCode(enum.Enum):
    """ """

    OP_CONSTANT = "OP_CONSTANT"
    OP_POP = "OP_POP"
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


def compile(composer: Compiler) -> List[ByteCode]:
    """ """
    bytecode: List[ByteCode] = []
    listing = init_locals()

    for statement in composer.statements:
        individual_bytecode, listing = execute(statement, listing)
        bytecode += individual_bytecode

    return bytecode


def execute(statement: statem.Statem, listing: Locals) -> Tuple[List[ByteCode], Locals]:
    """ """
    bytecode: List[ByteCode] = []

    if isinstance(statement, statem.Block):
        return execute_block(statement.statements, listing)

    if isinstance(statement, statem.Expression):
        individual_bytecode, listing = evaluate(statement.expression, listing)
        bytecode += individual_bytecode
        bytecode.append(OpCode.OP_POP)

        return bytecode, listing

    elif isinstance(statement, statem.Print):
        individual_bytecode, listing = evaluate(statement.expression, listing)
        bytecode += individual_bytecode
        bytecode.append(OpCode.OP_PRINT)

        return bytecode, listing

    raise Exception


def execute_block(
    statements: List[statem.Statem], listing: Locals
) -> Tuple[List[ByteCode], Locals]:
    """ """
    bytecode: List[ByteCode] = []

    for statement in statements:
        individual_bytecode, listing = execute(statement, listing)
        bytecode += individual_bytecode

    return bytecode, listing


def evaluate(expression: expr.Expr, listing: Locals) -> Tuple[List[ByteCode], Locals]:
    """ """
    bytecode: List[ByteCode] = []

    if isinstance(expression, expr.Binary):
        left_bytecode, listing = evaluate(expression.left, listing)
        right_bytecode, listing = evaluate(expression.right, listing)

        bytecode += left_bytecode
        bytecode += right_bytecode

        operator = operator_mapping[expression.operator.token_type]
        bytecode.append(operator)

        return bytecode, listing

    elif isinstance(expression, expr.Grouping):
        individual_bytecode, listing = evaluate(expression.expression, listing)
        bytecode += individual_bytecode

        return bytecode, listing

    elif isinstance(expression, expr.Literal):
        bytecode.append(OpCode.OP_CONSTANT)
        bytecode.append(expression.value)

        return bytecode, listing

    elif isinstance(expression, expr.Unary):
        individual_bytecode, listing = evaluate(expression.right, listing)
        bytecode += individual_bytecode
        bytecode.append(OpCode.OP_NEGATE)

        return bytecode, listing

    raise Exception
