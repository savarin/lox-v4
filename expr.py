from typing import Optional
import abc
import dataclasses

import token_class
import token_type


class Expr(abc.ABC):
    def evaluate(self) -> Optional[int]:
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
