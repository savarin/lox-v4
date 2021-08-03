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
    processor = parser.init_parser(tokens=tokens, debug_level=1)
    statements = parser.parse(processor)

    printer.pprint(statements, counter=1)
    return statements


def compile(statements: List[statem.Statem]) -> List[compiler.ByteCode]:
    """ """
    composer = compiler.init_compiler(statements=statements)
    bytecode = compiler.compile(composer)

    printer.pprint(bytecode, counter=1)
    return bytecode


def run(
    statements: List[statem.Statem],
    bytecode: Optional[List[compiler.ByteCode]],
    ecosystem: Optional[environment.Environment],
) -> environment.Environment:
    """ """
    if bytecode is not None:
        emulator = vm.init_vm(bytecode=bytecode)
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
        # bytecode = compile(statements)

        print("\n<output>")
        # run(statements, bytecode)
        ecosystem = run(statements, None, ecosystem)

        print("")
