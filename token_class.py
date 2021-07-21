from typing import Optional
import dataclasses

import token_type


@dataclasses.dataclass
class Token:
    """ """

    token_type: token_type.TokenType
    lexeme: str
    literal: Optional[int]

    def __str__(self) -> str:
        """ """
        return f"{self.token_type} {self.lexeme} {self.literal}"
