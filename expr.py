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

    def evaluate(self) -> Optional[int]:
        """ """
        left = self.left.evaluate()
        right = self.right.evaluate()
        individual_token = self.operator.token_type

        if individual_token == token_type.TokenType.MINUS:
            assert left is not None and right is not None
            return left - right

        elif individual_token == token_type.TokenType.PLUS:
            assert left is not None and right is not None
            return left + right

        if individual_token == token_type.TokenType.SLASH:
            assert left is not None and right is not None
            return left // right

        elif individual_token == token_type.TokenType.STAR:
            assert left is not None and right is not None
            return left * right

        return None


@dataclasses.dataclass
class Grouping(Expr):
    """ """

    expression: Expr

    def evaluate(self) -> Optional[int]:
        """ """
        return self.expression.evaluate()


@dataclasses.dataclass
class Literal(Expr):
    """ """

    value: int

    def evaluate(self) -> int:
        """ """
        return self.value


@dataclasses.dataclass
class Unary(Expr):
    """ """

    operator: token_class.Token
    right: Expr

    def evaluate(self) -> Optional[int]:
        """ """
        right = self.right.evaluate()
        individual_token = self.operator.token_type

        if individual_token == token_type.TokenType.MINUS:
            assert right is not None
            return -right

        return None
