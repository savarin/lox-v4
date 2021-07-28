from typing import Dict, Optional
import dataclasses

import token_class


@dataclasses.dataclass
class Environment:
    """ """

    values: Optional[Dict[str, Optional[int]]] = None


def init_environment() -> Environment:
    """ """
    values: Dict[str, Optional[int]] = {}

    return Environment(values=values)


def define(enclosure: Environment, name: str, value: Optional[int]) -> Environment:
    """ """
    assert enclosure.values is not None
    enclosure.values[name] = value

    return enclosure


def get(enclosure: Environment, individual_token: token_class.Token) -> Optional[int]:
    """ """
    assert enclosure.values is not None
    lexeme = individual_token.lexeme

    if lexeme in enclosure.values:
        return enclosure.values[lexeme]

    raise Exception


def assign(
    enclosure: Environment, name: token_class.Token, value: Optional[int]
) -> Environment:
    """ """
    assert enclosure.values is not None
    lexeme = name.lexeme

    if lexeme in enclosure.values:
        enclosure.values[lexeme] = value
        return enclosure

    raise Exception
