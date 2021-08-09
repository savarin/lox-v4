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


def compile(statements: List[statem.Statem]) -> compiler.Function:
    """ """
    composer = compiler.init_compiler(statements=statements)
    function = compiler.compile(composer)

    bytecode, values = function.bytecode, function.values
    assert values is not None

    printer.pprint(bytecode, counter=1, values=values)
    return function


def run(
    statements: List[statem.Statem],
    function: Optional[compiler.Function],
    ecosystem: Optional[environment.Environment],
) -> environment.Environment:
    """ """
    if function is not None:
        emulator = vm.init_vm(function=function)
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
        function = None

        try:
            function = compile(statements)
        except Exception:
            print("\033[91m    Error: No existing implementation.\033[0m")

        print("\n<output>")
        ecosystem = run(statements, function, ecosystem)

        print("")
