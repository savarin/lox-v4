import compiler
import parser
import scanner
import vm


def source_to_result(source: str) -> int:
    """ """
    searcher = scanner.init_scanner(source=source)
    tokens = scanner.scan(searcher)
    processor = parser.init_parser(tokens=tokens)
    statements = parser.parse(processor)
    composer = compiler.init_compiler(statements=statements)
    bytecode, _ = compiler.compile(composer)
    emulator = vm.init_vm(bytecode=bytecode)
    result = vm.run(emulator)[0]

    assert isinstance(result, int)
    return result


def test_run() -> None:
    """ """
    pass
    # assert source_to_result(source="1 - (2 + 3);") == -4
    # assert source_to_result(source="5 * (2 - (3 + 4));") == -25
