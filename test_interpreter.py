import interpreter
import parser
import scanner


def source_to_value(source: str) -> int:
    """ """
    searcher = scanner.init_scanner(source=source)
    tokens = scanner.scan(searcher)
    processor = parser.init_parser(tokens=tokens)
    statements = parser.parse(processor)
    inspector = interpreter.init_interpreter(statements=statements)
    return interpreter.interpret(inspector)[0][0]


def test_interpret() -> None:
    """ """
    assert source_to_value(source="1 - (2 + 3);") == -4
    assert source_to_value(source="5 * (2 - (3 + 4));") == -25
