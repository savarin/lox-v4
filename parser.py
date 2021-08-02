from typing import List, Optional, Tuple
import dataclasses

import expr
import statem
import token_class
import token_type


class ParseError(Exception):
    pass


@dataclasses.dataclass
class Parser:
    """ """

    tokens: List[token_class.Token]
    current: int = 0
    debug_level: int = 0
    debug_log: Optional[List[str]] = None


def init_parser(tokens: List[token_class.Token], debug_level: int = 0) -> Parser:
    """ """
    debug_log: List[str] = []
    return Parser(tokens=tokens, debug_level=debug_level, debug_log=debug_log)


def parse(processor: Parser) -> List[statem.Statem]:
    """ """
    statements: List[statem.Statem] = []

    while not is_at_end(processor):
        processor, individual_statement = declaration(processor)

        if individual_statement is not None:
            statements.append(individual_statement)

    return statements


def declaration(processor: Parser) -> Tuple[Parser, Optional[statem.Statem]]:
    """ """
    try:
        processor, is_match = match(processor, [token_type.TokenType.FUN])

        if is_match:
            return function(processor, "function")

        processor, is_match = match(processor, [token_type.TokenType.LET])

        if is_match:
            return var_declaration(processor)

        return statement(processor)

    except ParseError:
        return synchronize(processor), None


def function(processor: Parser, kind: str) -> Tuple[Parser, statem.Statem]:
    """ """
    processor, name = consume(
        processor, token_type.TokenType.IDENTIFIER, f"Expect {kind} name."
    )

    processor, _ = consume(
        processor, token_type.TokenType.LEFT_PAREN, f"Expect '(' after {kind} name."
    )

    parameters: List[token_class.Token] = []

    if not check(processor, token_type.TokenType.RIGHT_PAREN):
        while True:
            processor, parameter = consume(
                processor, token_type.TokenType.IDENTIFIER, "Expect parameter name."
            )
            parameters.append(parameter)

            processor, is_match = match(processor, [token_type.TokenType.COMMA])

            if not is_match:
                break

    processor, _ = consume(
        processor, token_type.TokenType.RIGHT_PAREN, "Expect ')' after parameters."
    )

    processor, _ = consume(
        processor, token_type.TokenType.LEFT_BRACE, "Expect '{' before body."
    )

    processor, body = block(processor)
    return processor, statem.Function(name, parameters, body)


def var_declaration(processor: Parser) -> Tuple[Parser, statem.Statem]:
    """ """
    processor, name = consume(
        processor, token_type.TokenType.IDENTIFIER, "Expect variable name."
    )

    initializer = None
    processor, is_match = match(processor, [token_type.TokenType.EQUAL])

    if is_match:
        processor, initializer = expression(processor)

    processor, _ = consume(
        processor,
        token_type.TokenType.SEMICOLON,
        "Expect ';' after variable declaration.",
    )

    return processor, statem.Var(name, initializer)


def statement(processor: Parser) -> Tuple[Parser, statem.Statem]:
    """ """
    processor, is_match = match(processor, [token_type.TokenType.IF])

    if is_match:
        return if_statement(processor)

    processor, is_match = match(processor, [token_type.TokenType.PRINT])

    if is_match:
        return print_statement(processor)

    processor, is_match = match(processor, [token_type.TokenType.RETURN])

    if is_match:
        return return_statement(processor)

    processor, is_match = match(processor, [token_type.TokenType.LEFT_BRACE])

    if is_match:
        processor, statements = block(processor)
        return processor, statem.Block(statements)

    return expression_statement(processor)


def if_statement(processor: Parser) -> Tuple[Parser, statem.Statem]:
    """ """
    processor, _ = consume(
        processor, token_type.TokenType.LEFT_PAREN, "Expect '(' after 'if'."
    )

    processor, condition = expression(processor)

    processor, _ = consume(
        processor, token_type.TokenType.RIGHT_PAREN, "Expect ')' after if condition."
    )

    processor, then_branch = statement(processor)

    else_branch = None

    processor, is_match = match(processor, [token_type.TokenType.ELSE])

    if is_match:
        processor, else_branch = statement(processor)

    return processor, statem.If(condition, then_branch, else_branch)


def print_statement(processor: Parser) -> Tuple[Parser, statem.Statem]:
    """ """
    processor, individual_expression = expression(processor)
    processor, _ = consume(
        processor, token_type.TokenType.SEMICOLON, "Expect ';' after print statement."
    )

    return processor, statem.Print(individual_expression)


def return_statement(processor: Parser) -> Tuple[Parser, statem.Return]:
    keyword = previous(processor)
    value = None

    if not check(processor, token_type.TokenType.SEMICOLON):
        processor, value = expression(processor)

    processor, _ = consume(
        processor, token_type.TokenType.SEMICOLON, "Expect ';' after return value."
    )

    return processor, statem.Return(keyword, value)


def block(processor: Parser) -> Tuple[Parser, List[statem.Statem]]:
    """ """
    statements: List[statem.Statem] = []

    while not check(processor, token_type.TokenType.RIGHT_BRACE) and not is_at_end(
        processor
    ):
        processor, individual_statement = declaration(processor)

        if individual_statement is not None:
            statements.append(individual_statement)

    processor, _ = consume(
        processor, token_type.TokenType.RIGHT_BRACE, "Expect '}' after block."
    )

    return processor, statements


def expression_statement(processor: Parser) -> Tuple[Parser, statem.Statem]:
    """ """
    processor, individual_expression = expression(processor)
    processor, _ = consume(
        processor, token_type.TokenType.SEMICOLON, "Expect ';' after expression."
    )

    return processor, statem.Expression(individual_expression)


def expression(processor: Parser) -> Tuple[Parser, expr.Expr]:
    """ """
    return assignment(processor)


def assignment(processor: Parser) -> Tuple[Parser, expr.Expr]:
    """ """
    processor, term_expression = equality(processor)
    processor, is_match = match(processor, [token_type.TokenType.EQUAL])

    if is_match:
        equals = previous(processor)
        processor, value = assignment(processor)

        if isinstance(term_expression, expr.Variable):
            name = term_expression.name
            return processor, expr.Assign(name, value)

        raise error(processor, equals, "Invalid assignment target.")

    return processor, term_expression


def equality(processor: Parser) -> Tuple[Parser, expr.Expr]:
    """ """
    processor, comparison_expression = comparison(processor)

    while True:
        processor, is_match = match(
            processor,
            [token_type.TokenType.BANG_EQUAL, token_type.TokenType.EQUAL_EQUAL],
        )

        if not is_match:
            break

        operator = previous(processor)
        processor, right = comparison(processor)
        comparison_expression = expr.Binary(comparison_expression, operator, right)

    return processor, comparison_expression


def comparison(processor: Parser) -> Tuple[Parser, expr.Expr]:
    """ """
    processor, term_expression = term(processor)

    while True:
        processor, is_match = match(
            processor,
            [
                token_type.TokenType.GREATER,
                token_type.TokenType.GREATER_EQUAL,
                token_type.TokenType.LESS,
                token_type.TokenType.LESS_EQUAL,
            ],
        )

        if not is_match:
            break

        operator = previous(processor)
        processor, right = term(processor)
        term_expression = expr.Binary(term_expression, operator, right)

    return processor, term_expression


def term(processor: Parser) -> Tuple[Parser, expr.Expr]:
    """ """
    processor, factor_expression = factor(processor)

    while True:
        processor, is_match = match(
            processor, [token_type.TokenType.MINUS, token_type.TokenType.PLUS]
        )

        if not is_match:
            break

        operator = previous(processor)
        processor, right = factor(processor)
        factor_expression = expr.Binary(factor_expression, operator, right)

    return processor, factor_expression


def factor(processor: Parser) -> Tuple[Parser, expr.Expr]:
    """ """
    processor, unary_expression = unary(processor)

    while True:
        processor, is_match = match(
            processor, [token_type.TokenType.SLASH, token_type.TokenType.STAR]
        )

        if not is_match:
            break

        operator = previous(processor)
        processor, right = unary(processor)
        unary_expression = expr.Binary(unary_expression, operator, right)

    return processor, unary_expression


def unary(processor: Parser) -> Tuple[Parser, expr.Expr]:
    """ """
    while True:
        processor, is_match = match(processor, [token_type.TokenType.MINUS])

        if not is_match:
            break

        operator = previous(processor)
        processor, right = unary(processor)
        return processor, expr.Unary(operator, right)

    return call(processor)


def call(processor: Parser) -> Tuple[Parser, expr.Expr]:
    """ """
    processor, primary_expression = primary(processor)

    while True:
        processor, is_match = match(processor, [token_type.TokenType.LEFT_PAREN])

        if is_match:
            processor, primary_expression = finish_call(processor, primary_expression)
        else:
            break

    return processor, primary_expression


def finish_call(processor: Parser, callee: expr.Expr) -> Tuple[Parser, expr.Expr]:
    """ """
    arguments: List[expr.Expr] = []

    if not check(processor, token_type.TokenType.RIGHT_PAREN):
        while True:
            processor, individual_expression = expression(processor)
            arguments.append(individual_expression)

            processor, is_match = match(processor, [token_type.TokenType.COMMA])

            if not is_match:
                break

    processor, paren = consume(
        processor, token_type.TokenType.RIGHT_PAREN, "Expect ')' after arguments."
    )

    return processor, expr.Call(callee, paren, arguments)


def primary(processor: Parser) -> Tuple[Parser, expr.Expr]:
    """ """
    processor, is_match = match(processor, [token_type.TokenType.NUMBER])

    if is_match:
        value = previous(processor).literal

        assert value is not None
        return processor, expr.Literal(value)

    processor, is_match = match(processor, [token_type.TokenType.IDENTIFIER])

    if is_match:
        individual_token = previous(processor)
        return processor, expr.Variable(individual_token)

    processor, is_match = match(processor, [token_type.TokenType.LEFT_PAREN])

    if is_match:
        processor, parenthesis_expression = term(processor)
        processor, _ = consume(
            processor, token_type.TokenType.RIGHT_PAREN, "Expect ')' after expression."
        )

        return processor, expr.Grouping(parenthesis_expression)

    raise error(processor, peek(processor), "Expect valid expression.")


def match(
    processor: Parser, token_types: List[token_type.TokenType]
) -> Tuple[Parser, bool]:
    """ """
    for individual_type in token_types:
        if check(processor, individual_type):
            processor, _ = advance(processor)
            return processor, True

    return processor, False


def consume(
    processor: Parser, individual_type: token_type.TokenType, message: str
) -> Tuple[Parser, token_class.Token]:
    """ """
    if check(processor, individual_type):
        return advance(processor)

    raise error(processor, peek(processor), message)


def advance(processor: Parser) -> Tuple[Parser, token_class.Token]:
    """ """
    if not is_at_end(processor):
        processor.current += 1

    return processor, previous(processor)


def check(processor: Parser, individual_type: token_type.TokenType) -> bool:
    """ """
    if is_at_end(processor):
        return False

    return peek(processor).token_type == individual_type


def peek(processor: Parser) -> token_class.Token:
    """ """
    return processor.tokens[processor.current]


def previous(processor: Parser) -> token_class.Token:
    """ """
    return processor.tokens[processor.current - 1]


def is_at_end(processor: Parser) -> bool:
    """ """
    return peek(processor).token_type == token_type.TokenType.EOF


def error(
    processor: Parser, individual_token: token_class.Token, message: str
) -> ParseError:
    """ """
    print(
        f"\033[91mError at TokenType.{individual_token.token_type.name} in line {individual_token.line}: {message}\033[0m"
    )
    return ParseError()


def synchronize(processor: Parser) -> Parser:
    """ """
    processor, _ = advance(processor)

    while not is_at_end(processor):
        if previous(processor).token_type == token_type.TokenType.SEMICOLON:
            return processor

        individual_type = peek(processor).token_type

        if individual_type in [
            token_type.TokenType.IF,
            token_type.TokenType.LET,
            token_type.TokenType.PRINT,
        ]:
            return processor

        processor, _ = advance(processor)

    return processor
