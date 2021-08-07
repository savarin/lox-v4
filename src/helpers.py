from typing import Optional, Union


Result = Union[int, str, None]


def is_truthy(operand: Result) -> bool:
    """ """
    if operand is None:
        return False

    elif isinstance(operand, bool):
        return operand

    return True


def is_equal(a: Optional[int], b: Optional[int]) -> bool:
    """ """
    if a is None and b is None:
        return True

    elif a is None or b is None:
        return False

    return a == b


def stringify(operand: Optional[int]) -> str:
    """ """
    if operand is None:
        return "nil"

    return str(operand)
