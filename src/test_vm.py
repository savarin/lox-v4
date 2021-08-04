from typing import Union
import compiler
import parser
import scanner
import vm


def source_to_result(source: str) -> Union[int, str]:
    """ """
    searcher = scanner.init_scanner(source=source)
    tokens = scanner.scan(searcher)
    processor = parser.init_parser(tokens=tokens)
    statements = parser.parse(processor)
    composer = compiler.init_compiler(statements=statements)
    bytecode, values = compiler.compile(composer)
    emulator = vm.init_vm(bytecode=bytecode, values=values)
    result = vm.run(emulator)[0]

    assert result is not None
    return result


def test_expression() -> None:
    """ """
    assert source_to_result(source="1 - (2 + 3);") == -4
    assert source_to_result(source="5 * (2 - (3 + 4));") == -25


def test_assignment() -> None:
    """ """
    assert source_to_result("let a; print a;") == "nil"
