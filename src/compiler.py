from typing import Dict, List, Union
import dataclasses
import enum

import expr
import statem
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
class Compiler:
    """ """

    statements: List[statem.Statem]


def init_compiler(statements: List[statem.Statem]) -> Compiler:
    """ """
    return Compiler(statements=statements)


def compile(composer: Compiler) -> List[ByteCode]:
    """ """
    bytecode: List[ByteCode] = []

    for statement in composer.statements:
        individual_bytecode = execute(statement)
        bytecode += individual_bytecode

    return bytecode


def execute(statement: statem.Statem) -> List[ByteCode]:
    """ """
    if isinstance(statement, statem.Block):
        return execute_block(statement.statements)

    if isinstance(statement, statem.Expression):
        bytecode = evaluate(statement.expression)
        bytecode.append(OpCode.OP_POP)

        return bytecode

    elif isinstance(statement, statem.Print):
        bytecode = evaluate(statement.expression)
        bytecode.append(OpCode.OP_PRINT)

        return bytecode

    raise Exception


def execute_block(statements: List[statem.Statem]) -> List[ByteCode]:
    """ """
    bytecode: List[ByteCode] = []

    for statement in statements:
        individual_bytecode = execute(statement)
        bytecode += individual_bytecode

    return bytecode


def evaluate(expression: expr.Expr) -> List[ByteCode]:
    """ """
    bytecode: List[ByteCode] = []

    if isinstance(expression, expr.Binary):
        bytecode += evaluate(expression.left)
        bytecode += evaluate(expression.right)

        operator = operator_mapping[expression.operator.token_type]
        bytecode.append(operator)

    elif isinstance(expression, expr.Grouping):
        bytecode += evaluate(expression.expression)

    elif isinstance(expression, expr.Literal):
        bytecode.append(OpCode.OP_CONSTANT)
        bytecode.append(expression.value)

    elif isinstance(expression, expr.Unary):
        bytecode += evaluate(expression.right)
        bytecode.append(OpCode.OP_NEGATE)

    return bytecode
