from typing import List, Tuple

import expr
import compiler
import interpreter
import parser
import scanner
import statem
import token_class
import vm


def pprint(statements: List[statem.Statem], counter: int = 0) -> None:
    """ """
    result: List[Tuple[str, int]] = []

    def traverse(expression: expr.Expr, counter: int):
        """ """
        if isinstance(expression, expr.Assign):
            result.append((f"Assign {expression.name.lexeme}", counter))
            traverse(expression.value, counter + 1)

        elif isinstance(expression, expr.Binary):
            result.append((f"Binary {expression.operator.lexeme}", counter))
            traverse(expression.left, counter + 1)
            traverse(expression.right, counter + 1)

        elif isinstance(expression, expr.Call):
            result.append(("Call", counter))
            traverse(expression.callee, counter + 1)

            for argument in expression.arguments:
                traverse(argument, counter + 2)

        elif isinstance(expression, expr.Grouping):
            result.append(("Grouping", counter))
            traverse(expression.expression, counter + 1)

        elif isinstance(expression, expr.Literal):
            result.append((f"Literal({expression.value})", counter))

        elif isinstance(expression, expr.Unary):
            result.append((f"Unary {expression.operator.lexeme}", counter))
            traverse(expression.right, counter + 1)

        elif isinstance(expression, expr.Variable):
            result.append((f"Variable {expression.name.lexeme}", counter))

    def expose(statement: statem.Statem, counter: int):
        """ """
        if isinstance(statement, statem.Block):
            result.append(("Block", counter))

            for block_statement in statement.statements:
                expose(block_statement, counter + 1)

        elif isinstance(statement, statem.Expression):
            result.append(("Expression", counter))
            traverse(statement.expression, counter + 1)

        elif isinstance(statement, statem.Function):
            result.append((f"Function {statement.name.lexeme}", counter))

            for function_statement in statement.body:
                expose(function_statement, counter + 1)

        elif isinstance(statement, statem.If):
            result.append(("If", counter))
            traverse(statement.condition, counter + 1)
            expose(statement.then_branch, counter + 1)

            if statement.else_branch is not None:
                expose(statement.else_branch, counter + 1)

        elif isinstance(statement, statem.Print):
            result.append(("Print", counter))
            traverse(statement.expression, counter + 1)

        elif isinstance(statement, statem.Return):
            result.append((f"Return", counter))

            if statement.value is not None:
                traverse(statement.value, counter + 1)

        elif isinstance(statement, statem.Var):
            result.append((f"Var {statement.name.lexeme}", counter))

            if statement.initializer is not None:
                traverse(statement.initializer, counter + 1)

    for statement in statements:
        expose(statement, counter=1)

    for item in result:
        print("    " * item[1] + item[0])


def scan(source: str) -> List[token_class.Token]:
    """ """
    searcher = scanner.init_scanner(source=source)
    tokens = scanner.scan(searcher)

    for individual_token in tokens:
        print(f"    TokenType.{individual_token.token_type._name_}")

    return tokens


def parse(tokens: List[token_class.Token]) -> List[statem.Statem]:
    """ """
    processor = parser.init_parser(tokens=tokens, debug_level=1)
    statements = parser.parse(processor)

    pprint(statements, counter=1)
    return statements


def compile(statements: List[statem.Statem]) -> List[compiler.ByteCode]:
    """ """
    composer = compiler.init_compiler(statements=statements)
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

    return bytecode


def run(statements: List[statem.Statem], bytecode: List[compiler.ByteCode]) -> None:
    """ """
    # emulator = vm.init_vm(bytecode=bytecode)
    inspector = interpreter.init_interpreter(statements=statements)

    # print(f"    compiled    : {vm.run(emulator)}")
    print(f"    interpreted : {interpreter.interpret(inspector)}")


if __name__ == "__main__":
    while True:
        # source = input("> ")
        source = """\
fun fib(n) {
    if (n <= 1) return n;
    return fib(n - 2) + fib(n - 1);
}

fib(9);"""
        # source = "fun count(n) { if (n > 1) count(n - 1); return n; } count(3);"

        if not source:
            break

        print("\n<input>")
        print(f"    {source}")

        print("\n<scanner>")
        tokens = scan(source)

        print("\n<parser>")
        statements = parse(tokens)

        # print("\n<compiler>")
        # bytecode = compile(statements)

        print("\n<output>")
        # run(statements, bytecode)
        run(statements, None)

        print("")
        break
