from typing import Optional

import expr
import interpreter
import parser
import scanner
import token_class
import token_type


def source_to_value(source: str) -> Optional[int]:
    """ """
    searcher = scanner.init_scanner(source=source)
    tokens = scanner.scan_tokens(searcher)
    processor = parser.init_parser(tokens=tokens)
    parse_tuple = parser.parse(processor)

    assert parse_tuple is not None
    inspector = interpreter.init_interpreter(expression=parse_tuple[1])
    return interpreter.interpret(inspector)


def test_interpret() -> None:
    """ """
    assert source_to_value(source="1 - (2 + 3)") == -4
    assert source_to_value(source="5 * (2 - (3 + 4))") == -25
