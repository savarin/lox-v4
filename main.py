import expr
import compiler
import interpreter
import parser
import scanner
import vm


def pprint(expression: expr.Expr) -> None:
    """ """
    result = []

    def traverse(expression: expr.Expr, counter: int = 1):
        """ """
        if isinstance(expression, expr.Literal):
            result.append((f"Literal({expression.value})", counter))

        elif isinstance(expression, expr.Grouping):
            result.append(("Grouping", counter))
            traverse(expression.expression, counter + 1)

        elif isinstance(expression, expr.Unary):
            result.append((f"Unary {expression.operator.lexeme}", counter))
            traverse(expression.right, counter + 1)

        elif isinstance(expression, expr.Binary):
            result.append((f"Binary {expression.operator.lexeme}", counter))
            traverse(expression.left, counter + 1)
            traverse(expression.right, counter + 1)

    traverse(expression)

    for item in result:
        print("    " * item[1] + item[0])


if __name__ == "__main__":
    while True:
        source = input("> ")

        if not source:
            break

        print(f"\n<input>\n    {source}")

        print("\n<scanner>")

        searcher = scanner.init_scanner(source=source)
        tokens = scanner.scan(searcher)

        for individual_token in tokens:
            print(f"    TokenType.{individual_token.token_type._name_}")

        print("\n<parser>")

        processor = parser.init_parser(tokens=tokens)
        parse_tuple = parser.parse(processor)
        assert parse_tuple is not None
        _, expression = parse_tuple

        pprint(expression)

        print("\n<compiler>")

        composer = compiler.init_compiler(expression=expression)
        bytecode = compiler.compile(composer)

        counter = 0

        while True:
            if counter >= len(bytecode):
                break

            individual_bytecode = bytecode[counter]
            assert not isinstance(individual_bytecode, int)
            print(f"    OpCode.{individual_bytecode._name_}", end=" ")
            counter += 1

            if individual_bytecode == compiler.OpCode.OP_CONSTANT:
                print(f"{str(bytecode[counter])}")
                counter += 1
            else:
                print("")

        emulator = vm.init_vm(bytecode=bytecode)
        print(f"\n<output>\n    compiled    : {vm.run(emulator)}")

        inspector = interpreter.init_interpreter(expression=expression)
        print(f"    interpreted : {interpreter.interpret(inspector)}\n")
