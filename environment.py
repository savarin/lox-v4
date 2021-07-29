from typing import Dict, Optional
import dataclasses

import token_class


@dataclasses.dataclass
class Environment:
    """ """

    enclosing: Optional["Environment"] = None
    values: Optional[Dict[str, Optional[int]]] = None


def init_environment(enclosing: Optional["Environment"] = None) -> Environment:
    """ """
    values: Dict[str, Optional[int]] = {}

    if enclosing is not None:
        individual_enclosing = enclosing.enclosing

        assert enclosing.values is not None
        individual_values = enclosing.values.copy()

        enclosing = Environment(
            enclosing=individual_enclosing, values=individual_values
        )

    return Environment(enclosing=enclosing, values=values)


def define(ecosystem: Environment, name: str, value: Optional[int]) -> Environment:
    """ """
    assert ecosystem.values is not None
    ecosystem.values[name] = value

    return ecosystem


def get(ecosystem: Environment, individual_token: token_class.Token) -> Optional[int]:
    """ """
    assert ecosystem.values is not None
    lexeme = individual_token.lexeme

    if lexeme in ecosystem.values:
        return ecosystem.values[lexeme]

    if ecosystem.enclosing is not None:
        return get(ecosystem.enclosing, individual_token)

    raise Exception


def assign(
    ecosystem: Environment, individual_token: token_class.Token, value: Optional[int]
) -> Environment:
    """ """
    assert ecosystem.values is not None
    lexeme = individual_token.lexeme

    if lexeme in ecosystem.values:
        ecosystem.values[lexeme] = value
        return ecosystem

    if ecosystem.enclosing is not None:
        ecosystem.enclosing = assign(ecosystem.enclosing, individual_token, value)
        return ecosystem

    raise Exception
