from typing import List, Optional, Tuple
import dataclasses
import functools

import expr
import statem
import token_class
import token_type


def expose(f):
    """ """

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if args[0].debug_level >= 1:
            args[0].debug_log.append(f.__name__)

        value = f(*args, **kwargs)
        return value

    return wrapper


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


@expose
def declaration(processor: Parser) -> Tuple[Parser, Optional[statem.Statem]]:
    """ """
    try:
        processor, is_match = match(processor, [token_type.TokenType.LET])

        if is_match:
            return var_declaration(processor)

        return statement(processor)

    except ParseError:
        return synchronize(processor), None


@expose
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


@expose
def statement(processor: Parser) -> Tuple[Parser, statem.Statem]:
    """ """
    processor, is_match = match(processor, [token_type.TokenType.PRINT])

    if is_match:
        return print_statement(processor)

    processor, is_match = match(processor, [token_type.TokenType.LEFT_BRACE])

    if is_match:
        processor, statements = block(processor)
        return processor, statem.Block(statements)

    return expression_statement(processor)


@expose
def print_statement(processor: Parser) -> Tuple[Parser, statem.Statem]:
    """ """
    processor, individual_expression = expression(processor)
    processor, _ = consume(
        processor, token_type.TokenType.SEMICOLON, "Expect ';' after print statement."
    )

    return processor, statem.Print(individual_expression)


@expose
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


@expose
def expression_statement(processor: Parser) -> Tuple[Parser, statem.Statem]:
    """ """
    processor, individual_expression = expression(processor)
    processor, _ = consume(
        processor, token_type.TokenType.SEMICOLON, "Expect ';' after expression."
    )

    return processor, statem.Expression(individual_expression)


@expose
def expression(processor: Parser) -> Tuple[Parser, expr.Expr]:
    """ """
    return assignment(processor)


@expose
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


@expose
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


@expose
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


@expose
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


@expose
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


@expose
def unary(processor: Parser) -> Tuple[Parser, expr.Expr]:
    """ """
    while True:
        processor, is_match = match(processor, [token_type.TokenType.MINUS])

        if not is_match:
            break

        operator = previous(processor)
        processor, right = unary(processor)
        return processor, expr.Unary(operator, right)

    return primary(processor)


@expose
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


def check(processor: Parser, individual_type: token_type.TokenType) -> bool:
    """ """
    if is_at_end(processor):
        return False

    return peek(processor).token_type == individual_type


def advance(processor: Parser) -> Tuple[Parser, token_class.Token]:
    """ """
    if not is_at_end(processor):
        processor.current += 1

    return processor, previous(processor)


def is_at_end(processor: Parser) -> bool:
    """ """
    return peek(processor).token_type == token_type.TokenType.EOF


def peek(processor: Parser) -> token_class.Token:
    """ """
    return processor.tokens[processor.current]


def previous(processor: Parser) -> token_class.Token:
    """ """
    return processor.tokens[processor.current - 1]


def error(
    processor: Parser, individual_token: token_class.Token, message: str
) -> ParseError:
    """ """
    print(f"Error at TokenType.{individual_token.token_type.name}: {message}")
    return ParseError()


def synchronize(processor: Parser) -> Parser:
    """ """
    processor, _ = advance(processor)

    while not is_at_end(processor):
        if previous(processor).token_type == token_type.TokenType.SEMICOLON:
            return processor

        individual_type = peek(processor).token_type

        if individual_type in [token_type.TokenType.LET, token_type.TokenType.PRINT]:
            return processor

        processor, _ = advance(processor)

    return processor
