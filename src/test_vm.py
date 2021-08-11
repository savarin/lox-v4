import compiler
import parser
import scanner
import vm


def source_to_result(source: str):
    """ """
    searcher = scanner.init_scanner(source=source)
    tokens = scanner.scan(searcher)
    processor = parser.init_parser(tokens=tokens)
    statements = parser.parse(processor)
    composer = compiler.init_compiler(statements=statements)
    function = compiler.compile(composer)
    emulator = vm.init_vm(function)
    result = vm.run(emulator)

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


def test_scope() -> None:
    """ """
    result = source_to_result(
        source="""\
let a = 1;
let b = 2;
let c = 3";
{
    let a = 10;
    let b = 20;
    {
        let a = 100;
        print a;
        print b;
        print c;
    }
    print a;
    print b;
    print c;
}
print a;
print b;
print c;"""
    )

    assert result[0] is None
    assert result[1] == "100"
    assert result[2] is None
    assert result[3] == "20"
    assert result[4] is None
    assert result[5] == "3"
    assert result[6] == 100
    assert result[7] is None
    assert result[8] == "10"
    assert result[9] is None
    assert result[10] == "20"
    assert result[11] is None
    assert result[12] == "3"
    assert result[13] == 20
    assert result[14] == 10
    assert result[15] is None
    assert result[16] == "1"
    assert result[17] is None
    assert result[18] == "2"
    assert result[19] is None
    assert result[20] == "3"


def test_basic_function() -> None:
    """ """
    result = source_to_result(source="fun add(a, b) { return a + b; } print add(1, 2);")

    assert result[0] is None
    assert result[1] is None
    assert result[2] == "3"
