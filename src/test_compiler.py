from typing import List, Tuple

import compiler
import parser
import scanner


def source_to_bytecode(source: str) -> Tuple[List[compiler.Byte], compiler.Values]:
    """ """
    searcher = scanner.init_scanner(source=source)
    tokens = scanner.scan(searcher)
    processor = parser.init_parser(tokens=tokens)
    statements = parser.parse(processor)
    composer = compiler.init_compiler(statements=statements)
    return compiler.compile(composer)


def test_expression() -> None:
    """ """
    bytecode, vector = source_to_bytecode(source="1 - (2 + 3);")

    assert bytecode[0] == compiler.OpCode.OP_CONSTANT
    assert bytecode[1] == 0
    assert bytecode[2] == compiler.OpCode.OP_CONSTANT
    assert bytecode[3] == 1
    assert bytecode[4] == compiler.OpCode.OP_CONSTANT
    assert bytecode[5] == 2
    assert bytecode[6] == compiler.OpCode.OP_ADD
    assert bytecode[7] == compiler.OpCode.OP_SUBTRACT
    assert bytecode[8] == compiler.OpCode.OP_POP

    assert vector.count == 3
    assert vector.array[0].value == 1
    assert vector.array[1].value == 2
    assert vector.array[2].value == 3

    bytecode, vector = source_to_bytecode(source="5 * (2 - (3 + 4));")

    assert bytecode[0] == compiler.OpCode.OP_CONSTANT
    assert bytecode[1] == 0
    assert bytecode[2] == compiler.OpCode.OP_CONSTANT
    assert bytecode[3] == 1
    assert bytecode[4] == compiler.OpCode.OP_CONSTANT
    assert bytecode[5] == 2
    assert bytecode[6] == compiler.OpCode.OP_CONSTANT
    assert bytecode[7] == 3
    assert bytecode[8] == compiler.OpCode.OP_ADD
    assert bytecode[9] == compiler.OpCode.OP_SUBTRACT
    assert bytecode[10] == compiler.OpCode.OP_MULTIPLY
    assert bytecode[11] == compiler.OpCode.OP_POP

    assert vector.count == 4
    assert vector.array[0].value == 5
    assert vector.array[1].value == 2
    assert vector.array[2].value == 3
    assert vector.array[3].value == 4


def test_assignment() -> None:
    """ """
    bytecode, vector = source_to_bytecode(source="let a; print a;")

    assert bytecode[0] == compiler.OpCode.OP_CONSTANT
    assert bytecode[1] is None
    assert bytecode[2] == compiler.OpCode.OP_GET
    assert bytecode[3] == 0
    assert bytecode[4] == compiler.OpCode.OP_PRINT

    assert vector.count == 0

    bytecode, vector = source_to_bytecode(source="let a = 1; print a;")

    assert bytecode[0] == compiler.OpCode.OP_CONSTANT
    assert bytecode[1] == 0
    assert bytecode[2] == compiler.OpCode.OP_GET
    assert bytecode[3] == 0
    assert bytecode[4] == compiler.OpCode.OP_PRINT

    assert vector.count == 1
    assert vector.array[0].value == 1

    bytecode, vector = source_to_bytecode(source="let a = 1; a = 2; print a + 3;")

    assert bytecode[0] == compiler.OpCode.OP_CONSTANT
    assert bytecode[1] == 0
    assert bytecode[2] == compiler.OpCode.OP_CONSTANT
    assert bytecode[3] == 1
    assert bytecode[4] == compiler.OpCode.OP_SET
    assert bytecode[5] == 0
    assert bytecode[6] == compiler.OpCode.OP_POP
    assert bytecode[7] == compiler.OpCode.OP_GET
    assert bytecode[8] == 0
    assert bytecode[9] == compiler.OpCode.OP_CONSTANT
    assert bytecode[10] == 2
    assert bytecode[11] == compiler.OpCode.OP_ADD
    assert bytecode[12] == compiler.OpCode.OP_PRINT

    assert vector.count == 3
    assert vector.array[0].value == 1
    assert vector.array[1].value == 2
    assert vector.array[2].value == 3
