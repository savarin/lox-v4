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

    assert len(bytecode) == 9
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

    assert len(bytecode) == 12
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

    assert len(bytecode) == 5
    assert bytecode[0] == compiler.OpCode.OP_CONSTANT
    assert bytecode[1] is None
    assert bytecode[2] == compiler.OpCode.OP_GET
    assert bytecode[3] == 1
    assert bytecode[4] == compiler.OpCode.OP_PRINT

    assert vector.count == 0

    bytecode, vector = source_to_bytecode(source="let a = 1; print a;")

    assert len(bytecode) == 5
    assert bytecode[0] == compiler.OpCode.OP_CONSTANT
    assert bytecode[1] == 0
    assert bytecode[2] == compiler.OpCode.OP_GET
    assert bytecode[3] == 1
    assert bytecode[4] == compiler.OpCode.OP_PRINT

    assert vector.count == 1
    assert vector.array[0].value == 1

    bytecode, vector = source_to_bytecode(source="let a = 1; a = 2; print a + 3;")

    assert len(bytecode) == 13
    assert bytecode[0] == compiler.OpCode.OP_CONSTANT
    assert bytecode[1] == 0
    assert bytecode[2] == compiler.OpCode.OP_CONSTANT
    assert bytecode[3] == 1
    assert bytecode[4] == compiler.OpCode.OP_SET
    assert bytecode[5] == 1
    assert bytecode[6] == compiler.OpCode.OP_POP
    assert bytecode[7] == compiler.OpCode.OP_GET
    assert bytecode[8] == 1
    assert bytecode[9] == compiler.OpCode.OP_CONSTANT
    assert bytecode[10] == 2
    assert bytecode[11] == compiler.OpCode.OP_ADD
    assert bytecode[12] == compiler.OpCode.OP_PRINT

    assert vector.count == 3
    assert vector.array[0].value == 1
    assert vector.array[1].value == 2
    assert vector.array[2].value == 3


def test_scope() -> None:
    """ """
    bytecode, vector = source_to_bytecode(
        source="""\
let a = 1;
{
    let a = 10;
    {
        let a = 100;
        print a;
    }
    print a;
}
print a;"""
    )

    assert len(bytecode) == 17
    assert bytecode[0] == compiler.OpCode.OP_CONSTANT
    assert bytecode[1] == 0
    assert bytecode[2] == compiler.OpCode.OP_CONSTANT
    assert bytecode[3] == 1
    assert bytecode[4] == compiler.OpCode.OP_CONSTANT
    assert bytecode[5] == 2
    assert bytecode[6] == compiler.OpCode.OP_GET
    assert bytecode[7] == 3
    assert bytecode[8] == compiler.OpCode.OP_PRINT
    assert bytecode[9] == compiler.OpCode.OP_POP
    assert bytecode[10] == compiler.OpCode.OP_GET
    assert bytecode[11] == 2
    assert bytecode[12] == compiler.OpCode.OP_PRINT
    assert bytecode[13] == compiler.OpCode.OP_POP
    assert bytecode[14] == compiler.OpCode.OP_GET
    assert bytecode[15] == 1
    assert bytecode[16] == compiler.OpCode.OP_PRINT

    assert vector.count == 3
    assert vector.array[0].value == 1
    assert vector.array[1].value == 10
    assert vector.array[2].value == 100


def test_basic_function() -> None:
    """ """
    bytecode, vector = source_to_bytecode(source="fun add(a, b) { print a + b; }")

    assert len(bytecode) == 2
    assert bytecode[0] == compiler.OpCode.OP_CONSTANT
    assert bytecode[1] == 0

    assert vector.count == 1

    function = vector.array[0].value
    assert isinstance(function, compiler.Function)
    assert function.function_type == compiler.FunctionType.TYPE_FUNCTION
    assert function.name == "add"

    bytecode = function.bytecode
    assert len(bytecode) == 8
    assert bytecode[0] == compiler.OpCode.OP_GET
    assert bytecode[1] == 1
    assert bytecode[2] == compiler.OpCode.OP_GET
    assert bytecode[3] == 2
    assert bytecode[4] == compiler.OpCode.OP_ADD
    assert bytecode[5] == compiler.OpCode.OP_PRINT
    assert bytecode[6] == compiler.OpCode.OP_POP
    assert bytecode[7] == compiler.OpCode.OP_POP
