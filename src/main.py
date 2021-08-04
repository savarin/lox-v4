from typing import List, Optional

import compiler
import environment
import interpreter
import parser
import printer
import scanner
import statem
import token_class
import vm


def scan(source: str) -> List[token_class.Token]:
    """ """
    searcher = scanner.init_scanner(source=source)
    tokens = scanner.scan(searcher)

    printer.pprint(tokens, counter=1)
    return tokens


def parse(tokens: List[token_class.Token]) -> List[statem.Statem]:
    """ """
    processor = parser.init_parser(tokens=tokens)
    statements = parser.parse(processor)

    printer.pprint(statements, counter=1)
    return statements


def compile(statements: List[statem.Statem]) -> List[compiler.Byte]:
    """ """
    composer = compiler.init_compiler(statements=statements)
    bytecode, values = compiler.compile(composer)

    printer.pprint(bytecode, counter=1, values=values)
    return bytecode


def run(
    statements: List[statem.Statem],
    bytecode: Optional[List[compiler.Byte]],
    values: Optional[compiler.Values],
    ecosystem: Optional[environment.Environment],
) -> environment.Environment:
    """ """
    if bytecode is not None and values is not None:
        emulator = vm.init_vm(bytecode=bytecode, values=values)
        print(f"    compiled    : {vm.run(emulator)}")

    inspector = interpreter.init_interpreter(statements=statements, ecosystem=ecosystem)
    print(f"    interpreted : {interpreter.interpret(inspector)}")

    assert inspector.ecosystem is not None
    return inspector.ecosystem


if __name__ == "__main__":
    ecosystem = None

    while True:
        source = input("> ")

        if not source:
            break

        print("\n<input>")
        print(f"    {source}")

        print("\n<scanner>")
        tokens = scan(source)

        print("\n<parser>")
        statements = parse(tokens)

        print("\n<compiler>")
        bytecode = compile(statements)

        print("\n<output>")
        ecosystem = run(statements, None, None, ecosystem)

        print("")
