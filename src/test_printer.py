from typing import List, Optional, Tuple

import compiler
import scanner
import token_class
import parser
import printer
import statem


ResultTuple = Tuple[
    List[token_class.Token], List[statem.Statem], Optional[List[compiler.ByteCode]]
]


def execute(source: str, convert_to_bytecode: bool = False) -> ResultTuple:
    """ """
    searcher = scanner.init_scanner(source=source)
    tokens = scanner.scan(searcher)

    processor = parser.init_parser(tokens=tokens)
    statements = parser.parse(processor)

    bytecode = None

    if convert_to_bytecode:
        composer = compiler.init_compiler(statements=statements)
        bytecode = compiler.compile(composer)

    return tokens, statements, bytecode


def test_expression():
    """ """
    source = "1 - (2 + 3);"
    tokens, statements, bytecode = execute(source, convert_to_bytecode=True)

    assert (
        "\n".join(printer.convert(tokens, counter=0))
        == """\
TokenType.NUMBER
TokenType.MINUS
TokenType.LEFT_PAREN
TokenType.NUMBER
TokenType.PLUS
TokenType.NUMBER
TokenType.RIGHT_PAREN
TokenType.SEMICOLON
TokenType.EOF"""
    )

    assert (
        "\n".join(printer.convert(statements, counter=0))
        == """\
Expression
    Binary -
        Literal(1)
        Grouping
            Binary +
                Literal(2)
                Literal(3)"""
    )

    assert (
        "\n".join(printer.convert(bytecode, counter=0))
        == """\
OpCode.OP_CONSTANT 1
OpCode.OP_CONSTANT 2
OpCode.OP_CONSTANT 3
OpCode.OP_ADD
OpCode.OP_SUBTRACT
OpCode.OP_POP"""
    )

    source = "5 * (2 - (3 + 4));"
    tokens, statements, bytecode = execute(source, convert_to_bytecode=True)

    assert (
        "\n".join(printer.convert(tokens, counter=0))
        == """\
TokenType.NUMBER
TokenType.STAR
TokenType.LEFT_PAREN
TokenType.NUMBER
TokenType.MINUS
TokenType.LEFT_PAREN
TokenType.NUMBER
TokenType.PLUS
TokenType.NUMBER
TokenType.RIGHT_PAREN
TokenType.RIGHT_PAREN
TokenType.SEMICOLON
TokenType.EOF"""
    )

    assert (
        "\n".join(printer.convert(statements, counter=0))
        == """\
Expression
    Binary *
        Literal(5)
        Grouping
            Binary -
                Literal(2)
                Grouping
                    Binary +
                        Literal(3)
                        Literal(4)"""
    )

    assert (
        "\n".join(printer.convert(bytecode, counter=0))
        == """\
OpCode.OP_CONSTANT 5
OpCode.OP_CONSTANT 2
OpCode.OP_CONSTANT 3
OpCode.OP_CONSTANT 4
OpCode.OP_ADD
OpCode.OP_SUBTRACT
OpCode.OP_MULTIPLY
OpCode.OP_POP"""
    )


def test_assignment() -> None:
    """ """
    source = "let a; print a;"
    tokens, statements, bytecode = execute(source)

    assert (
        "\n".join(printer.convert(tokens, counter=0))
        == """\
TokenType.LET
TokenType.IDENTIFIER
TokenType.SEMICOLON
TokenType.PRINT
TokenType.IDENTIFIER
TokenType.SEMICOLON
TokenType.EOF"""
    )

    assert (
        "\n".join(printer.convert(statements, counter=0))
        == """\
Var a
Print
    Variable a"""
    )

    source = "let a = 1; print a;"
    tokens, statements, bytecode = execute(source)

    assert (
        "\n".join(printer.convert(tokens, counter=0))
        == """\
TokenType.LET
TokenType.IDENTIFIER
TokenType.EQUAL
TokenType.NUMBER
TokenType.SEMICOLON
TokenType.PRINT
TokenType.IDENTIFIER
TokenType.SEMICOLON
TokenType.EOF"""
    )

    assert (
        "\n".join(printer.convert(statements, counter=0))
        == """\
Var a
    Literal(1)
Print
    Variable a"""
    )

    source = "let a = 1; a = 2; print a + 3;"
    tokens, statements, bytecode = execute(source)

    assert (
        "\n".join(printer.convert(tokens, counter=0))
        == """\
TokenType.LET
TokenType.IDENTIFIER
TokenType.EQUAL
TokenType.NUMBER
TokenType.SEMICOLON
TokenType.IDENTIFIER
TokenType.EQUAL
TokenType.NUMBER
TokenType.SEMICOLON
TokenType.PRINT
TokenType.IDENTIFIER
TokenType.PLUS
TokenType.NUMBER
TokenType.SEMICOLON
TokenType.EOF"""
    )

    assert (
        "\n".join(printer.convert(statements, counter=0))
        == """\
Var a
    Literal(1)
Expression
    Assign a
        Literal(2)
Print
    Binary +
        Variable a
        Literal(3)"""
    )


def test_scope():
    source = """\
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
print c;
"""

    tokens, statements, bytecode = execute(source)

    assert (
        "\n".join(printer.convert(tokens, counter=0))
        == """\
TokenType.LET
TokenType.IDENTIFIER
TokenType.EQUAL
TokenType.NUMBER
TokenType.SEMICOLON
TokenType.LET
TokenType.IDENTIFIER
TokenType.EQUAL
TokenType.NUMBER
TokenType.SEMICOLON
TokenType.LET
TokenType.IDENTIFIER
TokenType.EQUAL
TokenType.NUMBER
TokenType.SEMICOLON
TokenType.LEFT_BRACE
TokenType.LET
TokenType.IDENTIFIER
TokenType.EQUAL
TokenType.NUMBER
TokenType.SEMICOLON
TokenType.LET
TokenType.IDENTIFIER
TokenType.EQUAL
TokenType.NUMBER
TokenType.SEMICOLON
TokenType.LEFT_BRACE
TokenType.LET
TokenType.IDENTIFIER
TokenType.EQUAL
TokenType.NUMBER
TokenType.SEMICOLON
TokenType.PRINT
TokenType.IDENTIFIER
TokenType.SEMICOLON
TokenType.PRINT
TokenType.IDENTIFIER
TokenType.SEMICOLON
TokenType.PRINT
TokenType.IDENTIFIER
TokenType.SEMICOLON
TokenType.RIGHT_BRACE
TokenType.PRINT
TokenType.IDENTIFIER
TokenType.SEMICOLON
TokenType.PRINT
TokenType.IDENTIFIER
TokenType.SEMICOLON
TokenType.PRINT
TokenType.IDENTIFIER
TokenType.SEMICOLON
TokenType.RIGHT_BRACE
TokenType.PRINT
TokenType.IDENTIFIER
TokenType.SEMICOLON
TokenType.PRINT
TokenType.IDENTIFIER
TokenType.SEMICOLON
TokenType.PRINT
TokenType.IDENTIFIER
TokenType.SEMICOLON
TokenType.EOF"""
    )

    assert (
        "\n".join(printer.convert(statements, counter=0))
        == """\
Var a
    Literal(1)
Var b
    Literal(2)
Var c
    Literal(3)
Block
    Var a
        Literal(10)
    Var b
        Literal(20)
    Block
        Var a
            Literal(100)
        Print
            Variable a
        Print
            Variable b
        Print
            Variable c
    Print
        Variable a
    Print
        Variable b
    Print
        Variable c
Print
    Variable a
Print
    Variable b
Print
    Variable c"""
    )


def test_basic_function():
    """ """
    source = "fun add(a, b) { print a + b; } add(1, 2);"
    tokens, statements, bytecode = execute(source)

    assert (
        "\n".join(printer.convert(tokens, counter=0))
        == """\
TokenType.FUN
TokenType.IDENTIFIER
TokenType.LEFT_PAREN
TokenType.IDENTIFIER
TokenType.COMMA
TokenType.IDENTIFIER
TokenType.RIGHT_PAREN
TokenType.LEFT_BRACE
TokenType.PRINT
TokenType.IDENTIFIER
TokenType.PLUS
TokenType.IDENTIFIER
TokenType.SEMICOLON
TokenType.RIGHT_BRACE
TokenType.IDENTIFIER
TokenType.LEFT_PAREN
TokenType.NUMBER
TokenType.COMMA
TokenType.NUMBER
TokenType.RIGHT_PAREN
TokenType.SEMICOLON
TokenType.EOF"""
    )

    assert (
        "\n".join(printer.convert(statements, counter=0))
        == """\
Function add
    Print
        Binary +
            Variable a
            Variable b
Expression
    Call
        Variable add
            Literal(1)
            Literal(2)"""
    )


def test_recursive_function():
    """ """
    source = "fun count(n) { if (n> 1) count(n - 1); return n; } count(3);"
    tokens, statements, bytecode = execute(source)

    assert (
        "\n".join(printer.convert(tokens, counter=0))
        == """\
TokenType.FUN
TokenType.IDENTIFIER
TokenType.LEFT_PAREN
TokenType.IDENTIFIER
TokenType.RIGHT_PAREN
TokenType.LEFT_BRACE
TokenType.IF
TokenType.LEFT_PAREN
TokenType.IDENTIFIER
TokenType.GREATER
TokenType.NUMBER
TokenType.RIGHT_PAREN
TokenType.IDENTIFIER
TokenType.LEFT_PAREN
TokenType.IDENTIFIER
TokenType.MINUS
TokenType.NUMBER
TokenType.RIGHT_PAREN
TokenType.SEMICOLON
TokenType.RETURN
TokenType.IDENTIFIER
TokenType.SEMICOLON
TokenType.RIGHT_BRACE
TokenType.IDENTIFIER
TokenType.LEFT_PAREN
TokenType.NUMBER
TokenType.RIGHT_PAREN
TokenType.SEMICOLON
TokenType.EOF"""
    )

    assert (
        "\n".join(printer.convert(statements, counter=0))
        == """\
Function count
    If
        Binary >
            Variable n
            Literal(1)
        Expression
            Call
                Variable count
                    Binary -
                        Variable n
                        Literal(1)
    Return
        Variable n
Expression
    Call
        Variable count
            Literal(3)"""
    )

    source = (
        "fun fib(n) { if (n <= 1) return n; return fib(n - 2) + fib(n - 1); } fib(8);"
    )
    tokens, statements, bytecode = execute(source)

    assert (
        "\n".join(printer.convert(tokens, counter=0))
        == """\
TokenType.FUN
TokenType.IDENTIFIER
TokenType.LEFT_PAREN
TokenType.IDENTIFIER
TokenType.RIGHT_PAREN
TokenType.LEFT_BRACE
TokenType.IF
TokenType.LEFT_PAREN
TokenType.IDENTIFIER
TokenType.LESS_EQUAL
TokenType.NUMBER
TokenType.RIGHT_PAREN
TokenType.RETURN
TokenType.IDENTIFIER
TokenType.SEMICOLON
TokenType.RETURN
TokenType.IDENTIFIER
TokenType.LEFT_PAREN
TokenType.IDENTIFIER
TokenType.MINUS
TokenType.NUMBER
TokenType.RIGHT_PAREN
TokenType.PLUS
TokenType.IDENTIFIER
TokenType.LEFT_PAREN
TokenType.IDENTIFIER
TokenType.MINUS
TokenType.NUMBER
TokenType.RIGHT_PAREN
TokenType.SEMICOLON
TokenType.RIGHT_BRACE
TokenType.IDENTIFIER
TokenType.LEFT_PAREN
TokenType.NUMBER
TokenType.RIGHT_PAREN
TokenType.SEMICOLON
TokenType.EOF"""
    )

    assert (
        "\n".join(printer.convert(statements, counter=0))
        == """\
Function fib
    If
        Binary <=
            Variable n
            Literal(1)
        Return
            Variable n
    Return
        Binary +
            Call
                Variable fib
                    Binary -
                        Variable n
                        Literal(2)
            Call
                Variable fib
                    Binary -
                        Variable n
                        Literal(1)
Expression
    Call
        Variable fib
            Literal(8)"""
    )
