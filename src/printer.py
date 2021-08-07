from typing import List, Optional, Union, Tuple

import compiler
import expr
import statem
import token_class


Items = Union[List[token_class.Token], List[statem.Statem], List[compiler.Byte]]


def pprint(
    items: Items, counter: int = 0, values: Optional[compiler.Values] = None
) -> None:
    """ """
    for line in convert(items, counter, values):
        print(line)


def convert(
    items: Items, counter: int, values: Optional[compiler.Values] = None
) -> List[str]:
    """ """
    result: List[str] = []

    if len(items) == 0:
        return result

    if isinstance(items[0], token_class.Token):
        for individual_token in items:
            assert isinstance(individual_token, token_class.Token)
            result.append(
                indent(f"TokenType.{individual_token.token_type._name_}", counter)
            )

    elif isinstance(items[0], statem.Statem):
        statements: List[statem.Statem] = []

        for statement in items:
            assert isinstance(statement, statem.Statem)
            statements.append(statement)

        for parse_tuple in level(statements, counter):
            result.append(indent(parse_tuple[0], parse_tuple[1]))

    elif isinstance(items[0], compiler.OpCode):
        bytecode: List[compiler.Byte] = []
        current = 0

        for individual_bytecode in items:
            assert (
                isinstance(individual_bytecode, compiler.OpCode)
                or isinstance(individual_bytecode, int)
                or individual_bytecode is None
            )
            bytecode.append(individual_bytecode)

        while True:
            if current >= len(items):
                break

            individual_bytecode = items[current]

            assert isinstance(individual_bytecode, compiler.OpCode)
            line = indent(f"OpCode.{individual_bytecode._name_}", counter)
            current += 1

            if individual_bytecode in [
                compiler.OpCode.OP_CONSTANT,
                compiler.OpCode.OP_GET,
                compiler.OpCode.OP_SET,
            ]:
                location = items[current]
                value = None

                if location is not None:
                    assert isinstance(location, int)
                    assert values is not None
                    value = values.array[location].value

                assert isinstance(value, int) or value is None
                line += f" {str(value)}"
                current += 1

            elif individual_bytecode == compiler.OpCode.OP_JUMP:
                line += f" {items[current]}"
                current += 1

            elif individual_bytecode == compiler.OpCode.OP_JUMP_CONDITIONAL:
                line += f" {items[current]} {items[current + 1]}"
                current += 2

            result.append(line)

    return result


def indent(line: str, counter: int) -> str:
    """ """
    return "    " * counter + line


def level(statements: List[statem.Statem], counter: int) -> List[Tuple[str, int]]:
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
            result.append(("Return", counter))

            if statement.value is not None:
                traverse(statement.value, counter + 1)

        elif isinstance(statement, statem.Var):
            result.append((f"Var {statement.name.lexeme}", counter))

            if statement.initializer is not None:
                traverse(statement.initializer, counter + 1)

    for statement in statements:
        expose(statement, counter=counter)

    return result
