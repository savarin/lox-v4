from typing import List, Union

import interpreter
import parser
import scanner


def source_to_result(source: str) -> List[Union[int, str, None]]:
    """ """
    searcher = scanner.init_scanner(source=source)
    tokens = scanner.scan(searcher)
    processor = parser.init_parser(tokens=tokens)
    statements = parser.parse(processor)
    inspector = interpreter.init_interpreter(statements=statements)
    return interpreter.interpret(inspector)


def test_expression() -> None:
    """ """
    assert source_to_result(source="1 - (2 + 3);")[0] == -4
    assert source_to_result(source="5 * (2 - (3 + 4));")[0] == -25


def test_assignment() -> None:
    """ """
    result = source_to_result(source="let a; print a;")

    assert result[0] is None
    assert result[1] == ""

    result = source_to_result(source="let a = 1; print a;")

    assert result[0] is None
    assert result[1] == "1"

    result = source_to_result(source="let a = 1; a = 2; print a + 3;")

    assert result[0] is None
    assert result[1] is None
    assert result[2] == "5"


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
    assert result[1] is None
    assert result[2] is None
    assert result[3] is None
    assert result[4] is None
    assert result[5] is None

    assert result[6] == "100"
    assert result[7] == "20"
    assert result[8] == "3"

    assert result[9] == "10"
    assert result[10] == "20"
    assert result[11] == "3"

    assert result[12] == "1"
    assert result[13] == "2"
    assert result[14] == "3"
