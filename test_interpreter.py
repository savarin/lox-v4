from typing import List, Union

import interpreter
import parser
import scanner


def source_to_value(source: str) -> List[Union[int, str, None]]:
    """ """
    searcher = scanner.init_scanner(source=source)
    tokens = scanner.scan(searcher)
    processor = parser.init_parser(tokens=tokens)
    statements = parser.parse(processor)
    inspector = interpreter.init_interpreter(statements=statements)
    return interpreter.interpret(inspector)


def test_expression() -> None:
    """ """
    assert source_to_value(source="1 - (2 + 3);")[0] == -4
    assert source_to_value(source="5 * (2 - (3 + 4));")[0] == -25


def test_assignment() -> None:
    """ """
    statements = source_to_value(source="let a; print a;")

    assert statements[0] is None
    assert statements[1] == ""

    statements = source_to_value(source="let a = 1; print a;")

    assert statements[0] is None
    assert statements[1] == "1"

    statements = source_to_value(source="let a = 1; a = 2; print a + 3;")

    assert statements[0] is None
    assert statements[1] == 2
    assert statements[2] == "5"
