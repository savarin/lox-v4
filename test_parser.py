from typing import List

import expr
import parser
import scanner
import statem
import token_class
import token_type


def source_to_statements(source: str) -> List[statem.Statem]:
    """ """
    searcher = scanner.init_scanner(source=source)
    tokens = scanner.scan(searcher)
    processor = parser.init_parser(tokens=tokens)
    return parser.parse(processor)


def test_valid_expression() -> None:
    """ """
    statement = source_to_statements(source="1 - (2 + 3);")[0]
    assert isinstance(statement, statem.Expression)
    expression = statement.expression

    assert isinstance(expression, expr.Binary)
    assert isinstance(expression.left, expr.Literal)
    assert isinstance(expression.right, expr.Grouping)
    assert expression.operator.token_type == token_type.TokenType.MINUS

    assert isinstance(expression.right.expression, expr.Binary)
    assert isinstance(expression.right.expression.left, expr.Literal)
    assert isinstance(expression.right.expression.right, expr.Literal)
    assert expression.right.expression.operator.token_type == token_type.TokenType.PLUS

    statement = source_to_statements(source="5 * (-2 - (3 + 4));")[0]
    assert isinstance(statement, statem.Expression)
    expression = statement.expression

    assert isinstance(expression, expr.Binary)
    assert isinstance(expression.left, expr.Literal)
    assert isinstance(expression.right, expr.Grouping)
    assert expression.operator.token_type == token_type.TokenType.STAR

    assert isinstance(expression.right.expression, expr.Binary)
    assert isinstance(expression.right.expression.left, expr.Unary)
    assert isinstance(expression.right.expression.right, expr.Grouping)
    assert (
        expression.right.expression.left.operator.token_type
        == token_type.TokenType.MINUS
    )

    assert isinstance(expression.right.expression.right.expression, expr.Binary)
    assert isinstance(expression.right.expression.right.expression.left, expr.Literal)
    assert isinstance(expression.right.expression.right.expression.left, expr.Literal)
    assert (
        expression.right.expression.right.expression.operator.token_type
        == token_type.TokenType.PLUS
    )


def test_invalid_expression() -> None:
    """ """
    assert source_to_statements(source="1 +;") == []


def test_assignment() -> None:
    """ """
    statements = source_to_statements(source="let a; print a;")

    var_declaration = statements[0]
    assert isinstance(var_declaration, statem.Var)
    assert var_declaration.name.token_type == token_type.TokenType.IDENTIFIER
    assert var_declaration.name.lexeme == "a"
    assert var_declaration.name.literal is None
    assert var_declaration.initializer is None

    print_statement = statements[1]
    assert isinstance(print_statement, statem.Print)
    assert isinstance(print_statement.expression, expr.Variable)
    assert print_statement.expression.name.token_type == token_type.TokenType.IDENTIFIER
    assert print_statement.expression.name.lexeme == "a"
    assert print_statement.expression.name.literal is None

    statements = source_to_statements(source="let a = 1; print a;")

    var_declaration = statements[0]
    assert isinstance(var_declaration, statem.Var)
    assert var_declaration.name.token_type == token_type.TokenType.IDENTIFIER
    assert var_declaration.name.lexeme == "a"
    assert var_declaration.name.literal is None
    assert isinstance(var_declaration.initializer, expr.Literal)
    assert var_declaration.initializer.value == 1

    print_statement = statements[1]
    assert isinstance(print_statement, statem.Print)
    assert isinstance(print_statement.expression, expr.Variable)
    assert print_statement.expression.name.token_type == token_type.TokenType.IDENTIFIER
    assert print_statement.expression.name.lexeme == "a"
    assert print_statement.expression.name.literal is None

    statements = source_to_statements(source="let a = 1; a = 2; print a + 3;")

    var_declaration = statements[0]
    assert isinstance(var_declaration, statem.Var)
    assert var_declaration.name.token_type == token_type.TokenType.IDENTIFIER
    assert var_declaration.name.lexeme == "a"
    assert var_declaration.name.literal is None
    assert isinstance(var_declaration.initializer, expr.Literal)
    assert var_declaration.initializer.value == 1

    assignment = statements[1]
    assert isinstance(assignment, statem.Expression)
    assert isinstance(assignment.expression, expr.Assign)
    assert assignment.expression.name.token_type == token_type.TokenType.IDENTIFIER
    assert assignment.expression.name.lexeme == "a"
    assert assignment.expression.name.literal is None
    assert isinstance(assignment.expression.value, expr.Literal)
    assert assignment.expression.value.value == 2

    print_statement = statements[2]
    assert isinstance(print_statement, statem.Print)
    assert isinstance(print_statement.expression, expr.Binary)
    assert isinstance(print_statement.expression.left, expr.Variable)
    assert (
        print_statement.expression.left.name.token_type
        == token_type.TokenType.IDENTIFIER
    )
    assert print_statement.expression.left.name.lexeme == "a"
    assert print_statement.expression.left.name.literal is None
    assert print_statement.expression.operator.token_type == token_type.TokenType.PLUS
    assert isinstance(print_statement.expression.right, expr.Literal)
    assert print_statement.expression.right.value == 3


def test_scope() -> None:
    """ """
    statements = source_to_statements(
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

    var_declaration_first = statements[0]
    assert isinstance(var_declaration_first, statem.Var)
    assert var_declaration_first.name.token_type == token_type.TokenType.IDENTIFIER
    assert var_declaration_first.name.lexeme == "a"
    assert var_declaration_first.name.literal is None
    assert isinstance(var_declaration_first.initializer, expr.Literal)
    assert var_declaration_first.initializer.value == 1

    block_first = statements[1]
    assert isinstance(block_first, statem.Block)

    var_declaration_second = block_first.statements[0]
    assert isinstance(var_declaration_second, statem.Var)
    assert var_declaration_second.name.token_type == token_type.TokenType.IDENTIFIER
    assert var_declaration_second.name.lexeme == "a"
    assert var_declaration_second.name.literal is None
    assert isinstance(var_declaration_second.initializer, expr.Literal)
    assert var_declaration_second.initializer.value == 10

    block_second = block_first.statements[1]
    assert isinstance(block_second, statem.Block)

    var_declaration_third = block_second.statements[0]
    assert isinstance(var_declaration_third, statem.Var)
    assert var_declaration_third.name.token_type == token_type.TokenType.IDENTIFIER
    assert var_declaration_third.name.lexeme == "a"
    assert var_declaration_third.name.literal is None
    assert isinstance(var_declaration_third.initializer, expr.Literal)
    assert var_declaration_third.initializer.value == 100

    print_statement_first = block_second.statements[1]
    assert isinstance(print_statement_first, statem.Print)
    assert isinstance(print_statement_first.expression, expr.Variable)
    assert (
        print_statement_first.expression.name.token_type
        == token_type.TokenType.IDENTIFIER
    )
    assert print_statement_first.expression.name.lexeme == "a"
    assert print_statement_first.expression.name.literal is None

    print_statement_second = block_first.statements[2]
    assert isinstance(print_statement_second, statem.Print)
    assert isinstance(print_statement_second.expression, expr.Variable)
    assert (
        print_statement_second.expression.name.token_type
        == token_type.TokenType.IDENTIFIER
    )
    assert print_statement_second.expression.name.lexeme == "a"
    assert print_statement_second.expression.name.literal is None

    print_statement_third = block_first.statements[2]
    assert isinstance(print_statement_third, statem.Print)
    assert isinstance(print_statement_third.expression, expr.Variable)
    assert (
        print_statement_third.expression.name.token_type
        == token_type.TokenType.IDENTIFIER
    )
    assert print_statement_third.expression.name.lexeme == "a"
    assert print_statement_third.expression.name.literal is None


def test_basic_function() -> None:
    """ """
    statements = source_to_statements(
        source="fun add(a, b) { print a + b; } add(1, 2);"
    )

    function = statements[0]
    assert isinstance(function, statem.Function)
    assert function.name.lexeme == "add"
    assert function.parameters[0].lexeme == "a"
    assert function.parameters[1].lexeme == "b"

    body = function.body[0]
    assert isinstance(body, statem.Print)
    assert isinstance(body.expression, expr.Binary)
    assert isinstance(body.expression.operator, token_class.Token)
    assert body.expression.operator.lexeme == "+"
    assert isinstance(body.expression.left, expr.Variable)
    assert body.expression.left.name.lexeme == "a"
    assert isinstance(body.expression.right, expr.Variable)
    assert body.expression.right.name.lexeme == "b"

    call = statements[1]
    assert isinstance(call, statem.Expression)
    assert isinstance(call.expression, expr.Call)
    assert isinstance(call.expression.callee, expr.Variable)
    assert call.expression.callee.name.lexeme == "add"
    assert isinstance(call.expression.arguments[0], expr.Literal)
    assert call.expression.arguments[0].value == 1
    assert isinstance(call.expression.arguments[1], expr.Literal)
    assert call.expression.arguments[1].value == 2


def test_recursive_function() -> None:
    """ """
    statements = source_to_statements(
        source="fun count(n) { if (n> 1) count(n - 1); return n; } count(3);"
    )

    function = statements[0]
    assert isinstance(function, statem.Function)
    assert function.name.lexeme == "count"
    assert function.parameters[0].lexeme == "n"

    body = function.body[0]
    assert isinstance(body, statem.If)
    assert isinstance(body.condition, expr.Binary)
    assert body.condition.operator.lexeme == ">"
    assert isinstance(body.condition.left, expr.Variable)
    assert body.condition.left.name.lexeme == "n"
    assert isinstance(body.condition.right, expr.Literal)
    assert body.condition.right.value == 1

    then_branch = body.then_branch
    assert isinstance(then_branch, statem.Expression)
    assert isinstance(then_branch.expression, expr.Call)
    assert isinstance(then_branch.expression.callee, expr.Variable)
    assert then_branch.expression.callee.name.lexeme == "count"
    assert isinstance(then_branch.expression.arguments[0], expr.Binary)
    assert then_branch.expression.arguments[0].operator.lexeme == "-"
    assert isinstance(then_branch.expression.arguments[0].left, expr.Variable)
    assert then_branch.expression.arguments[0].left.name.lexeme == "n"
    assert isinstance(then_branch.expression.arguments[0].right, expr.Literal)
    assert then_branch.expression.arguments[0].right.value == 1

    else_branch = body.else_branch
    assert else_branch is None

    return_statement = function.body[1]
    assert isinstance(return_statement, statem.Return)
    assert isinstance(return_statement.keyword, token_class.Token)
    assert return_statement.keyword.lexeme == "return"
    assert isinstance(return_statement.value, expr.Variable)
    assert return_statement.value.name.lexeme == "n"

    expression = statements[1]
    assert isinstance(expression, statem.Expression)
    assert isinstance(expression.expression, expr.Call)
    assert isinstance(expression.expression.callee, expr.Variable)
    assert expression.expression.callee.name.lexeme == "count"
    assert isinstance(expression.expression.arguments[0], expr.Literal)
    assert expression.expression.arguments[0].value == 3

    statements = source_to_statements(
        source="fun fib(n) { if (n <= 1) return n; return fib(n - 2) + fib(n - 1); } fib(8);"
    )

    function = statements[0]
    assert isinstance(function, statem.Function)
    assert function.name.lexeme == "fib"
    assert function.parameters[0].lexeme == "n"

    body = function.body[0]
    assert isinstance(body, statem.If)
    assert isinstance(body.condition, expr.Binary)
    assert body.condition.operator.lexeme == "<="
    assert isinstance(body.condition.left, expr.Variable)
    assert body.condition.left.name.lexeme == "n"
    assert isinstance(body.condition.right, expr.Literal)
    assert body.condition.right.value == 1

    then_branch = body.then_branch
    assert isinstance(then_branch, statem.Return)
    assert isinstance(then_branch.value, expr.Variable)
    assert then_branch.value.name.lexeme == "n"

    return_statement = function.body[1]
    assert isinstance(return_statement, statem.Return)
    assert isinstance(return_statement.value, expr.Binary)
    assert return_statement.value.operator.lexeme == "+"

    left_call = return_statement.value.left
    assert isinstance(left_call, expr.Call)
    assert isinstance(left_call.callee, expr.Variable)
    assert left_call.callee.name.lexeme == "fib"
    assert isinstance(left_call.arguments[0], expr.Binary)
    assert left_call.arguments[0].operator.lexeme == "-"
    assert isinstance(left_call.arguments[0].left, expr.Variable)
    assert left_call.arguments[0].left.name.lexeme == "n"
    assert isinstance(left_call.arguments[0].right, expr.Literal)
    assert left_call.arguments[0].right.value == 2

    right_call = return_statement.value.right
    assert isinstance(right_call, expr.Call)
    assert isinstance(right_call.callee, expr.Variable)
    assert right_call.callee.name.lexeme == "fib"
    assert isinstance(right_call.arguments[0], expr.Binary)
    assert right_call.arguments[0].operator.lexeme == "-"
    assert isinstance(right_call.arguments[0].left, expr.Variable)
    assert right_call.arguments[0].left.name.lexeme == "n"
    assert isinstance(right_call.arguments[0].right, expr.Literal)
    assert right_call.arguments[0].right.value == 1

    expression = statements[1]
    assert isinstance(expression, statem.Expression)
    assert isinstance(expression.expression, expr.Call)
    assert isinstance(expression.expression.callee, expr.Variable)
    assert expression.expression.callee.name.lexeme == "fib"
    assert isinstance(expression.expression.arguments[0], expr.Literal)
    assert expression.expression.arguments[0].value == 8
