from typing import List

import compiler
import parser
import scanner


def source_to_bytecode(source: str) -> List[compiler.ByteCode]:
    """ """
    searcher = scanner.init_scanner(source=source)
    tokens = scanner.scan(searcher)
    processor = parser.init_parser(tokens=tokens)
    parse_tuple = parser.parse(processor)

    assert parse_tuple is not None
    composer = compiler.init_compiler(expression=parse_tuple[1])
    return compiler.compile(composer)


def test_compile() -> None:
    """ """
    bytecode = source_to_bytecode(source="1 - (2 + 3)")

    assert bytecode[0] == compiler.OpCode.OP_CONSTANT
    assert bytecode[1] == 1
    assert bytecode[2] == compiler.OpCode.OP_CONSTANT
    assert bytecode[3] == 2
    assert bytecode[4] == compiler.OpCode.OP_CONSTANT
    assert bytecode[5] == 3
    assert bytecode[6] == compiler.OpCode.OP_ADD
    assert bytecode[7] == compiler.OpCode.OP_SUBTRACT

    bytecode = source_to_bytecode(source="5 * (2 - (3 + 4))")

    assert bytecode[0] == compiler.OpCode.OP_CONSTANT
    assert bytecode[1] == 5
    assert bytecode[2] == compiler.OpCode.OP_CONSTANT
    assert bytecode[3] == 2
    assert bytecode[4] == compiler.OpCode.OP_CONSTANT
    assert bytecode[5] == 3
    assert bytecode[6] == compiler.OpCode.OP_CONSTANT
    assert bytecode[7] == 4
    assert bytecode[8] == compiler.OpCode.OP_ADD
    assert bytecode[9] == compiler.OpCode.OP_SUBTRACT
    assert bytecode[10] == compiler.OpCode.OP_MULTIPLY
