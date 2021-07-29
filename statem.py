from typing import List, Optional
import abc
import dataclasses

import expr
import token_class


class Statem(abc.ABC):
    """ """

    pass


@dataclasses.dataclass
class Block(Statem):
    """ """

    statements: List[Statem]


@dataclasses.dataclass
class Expression(Statem):
    """ """

    expression: expr.Expr


@dataclasses.dataclass
class Print(Statem):
    """ """

    expression: expr.Expr


@dataclasses.dataclass
class Var(Statem):
    """ """

    name: token_class.Token
    initializer: Optional[expr.Expr]
