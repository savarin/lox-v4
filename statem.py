import abc
import dataclasses

import expr


class Statem(abc.ABC):
    """ """

    pass


@dataclasses.dataclass
class Expression(Statem):
    """ """

    expression: expr.Expr


@dataclasses.dataclass
class Print(Statem):
    """ """

    expression: expr.Expr
