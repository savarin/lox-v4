from typing import List
import compiler
import helpers
import parser
import scanner
import vm


def source_to_result(source: str) -> List[helpers.Result]:
    """ """
    searcher = scanner.init_scanner(source=source)
    tokens = scanner.scan(searcher)
    processor = parser.init_parser(tokens=tokens)
    statements = parser.parse(processor)
    composer = compiler.init_compiler(statements=statements)
    bytecode, values = compiler.compile(composer)
    emulator = vm.init_vm(bytecode=bytecode, values=values)
    result = vm.run(emulator)

    assert result is not None
    return result


def test_expression() -> None:
    """ """
    result = source_to_result(source="1 - (2 + 3);")

    assert result[0] == -4

    result = source_to_result(source="5 * (2 - (3 + 4));")

    assert result[0] == -25


def test_assignment() -> None:
    """ """
    result = source_to_result("let a; print a;")

    assert result[0] is None
    assert result[1] == "nil"

    result = source_to_result(source="let a = 1; print a;")

    assert result[0] is None
    assert result[1] == "1"

    result = source_to_result(source="let a = 1; a = 2; print a + 3;")

    assert result[0] is None
    assert result[1] == 2
    assert result[2] is None
    assert result[3] == "5"
