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
    lexeme = individual_token.lexeme

    assert enclosure.values is not None
    assert lexeme in enclosure.values
    return enclosure.values[lexeme]
