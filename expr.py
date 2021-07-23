import abc
import dataclasses

import token_class


class Expr(abc.ABC):
    """ """

    pass


@dataclasses.dataclass
class Binary(Expr):
    """ """

    left: Expr
    operator: token_class.Token
    right: Expr


@dataclasses.dataclass
class Grouping(Expr):
    """ """

    expression: Expr


@dataclasses.dataclass
class Literal(Expr):
    """ """

    value: int


@dataclasses.dataclass
class Unary(Expr):
    """ """

    operator: token_class.Token
    right: Expr
