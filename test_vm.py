from typing import List, Optional, Union

import compiler
import expr
import parser
import scanner
import token_class
import token_type
import vm


def source_to_result(source: str) -> int:
    """ """
    searcher = scanner.init_scanner(source=source)
    tokens = scanner.scan_tokens(searcher)
    processor = parser.init_parser(tokens=tokens)
    parse_tuple = parser.parse(processor)

    assert parse_tuple is not None
    composer = compiler.init_compiler(expression=parse_tuple[1])
    bytecode = compiler.compile(composer)

    emulator = vm.init_vm(bytecode=bytecode)
    return vm.run(emulator)


def test_run() -> None:
    """ """
    assert source_to_result(source="1 - (2 + 3)") == -4
    assert source_to_result(source="5 * (2 - (3 + 4))") == -25
