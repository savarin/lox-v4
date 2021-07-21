from typing import Optional
import dataclasses

import expr


@dataclasses.dataclass
class Interpreter:
    """ """

    expression: expr.Expr


def init_interpreter(expression: expr.Expr) -> Interpreter:
    """ """
    return Interpreter(expression=expression)


def interpret(inspector: Interpreter) -> Optional[int]:
    """ """
    return inspector.expression.evaluate()
