from typing import Dict, List, Union
import dataclasses
import enum

import expr
import token_type


ByteCode = Union["OpCode", int]


class OpCode(enum.Enum):
    """ """

    OP_CONSTANT = "OP_CONSTANT"
    OP_POP = "OP_POP"
    OP_ADD = "OP_ADD"
    OP_SUBTRACT = "OP_SUBTRACT"
    OP_MULTIPLY = "OP_MULTIPLY"
    OP_DIVIDE = "OP_DIVIDE"
    OP_NEGATE = "OP_NEGATE"


operator_mapping: Dict[token_type.TokenType, OpCode] = {
    token_type.TokenType.PLUS: OpCode.OP_ADD,
    token_type.TokenType.MINUS: OpCode.OP_SUBTRACT,
    token_type.TokenType.STAR: OpCode.OP_MULTIPLY,
    token_type.TokenType.SLASH: OpCode.OP_DIVIDE,
}


@dataclasses.dataclass
class Compiler:
    """ """

    expression: expr.Expr


def init_compiler(expression: expr.Expr) -> Compiler:
    """ """
    return Compiler(expression=expression)


def compile(composer: Compiler) -> List[ByteCode]:
    """ """
    bytecode: List[ByteCode] = []

    def traverse(expression: expr.Expr):
        """ """
        if isinstance(expression, expr.Literal):
            bytecode.append(OpCode.OP_CONSTANT)
            bytecode.append(expression.value)

        elif isinstance(expression, expr.Grouping):
            traverse(expression.expression)

        elif isinstance(expression, expr.Unary):
            traverse(expression.right)
            bytecode.append(OpCode.OP_NEGATE)

        elif isinstance(expression, expr.Binary):
            traverse(expression.left)
            traverse(expression.right)

            operator = operator_mapping[expression.operator.token_type]
            bytecode.append(operator)

    traverse(composer.expression)
    return bytecode
