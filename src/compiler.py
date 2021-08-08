from typing import Dict, List, Optional, Tuple, Union
import dataclasses
import enum

import expr
import statem
import token_class
import token_type


Byte = Union["OpCode", int, None]


INT_COUNT = 16


class FunctionType(enum.Enum):
    """ """

    TYPE_FUNCTION = "TYPE_FUNCTION"
    TYPE_SCRIPT = "TYPE_SCRIPT"


class OpCode(enum.Enum):
    """ """

    OP_CONSTANT = "OP_CONSTANT"
    OP_POP = "OP_POP"
    OP_GET = "OP_GET"
    OP_SET = "OP_SET"
    OP_EQUAL = "OP_EQUAL"
    OP_GREATER = "OP_GREATER"
    OP_LESS = "OP_LESS"
    OP_ADD = "OP_ADD"
    OP_SUBTRACT = "OP_SUBTRACT"
    OP_MULTIPLY = "OP_MULTIPLY"
    OP_DIVIDE = "OP_DIVIDE"
    OP_NOT = "OP_NOT"
    OP_NEGATE = "OP_NEGATE"
    OP_PRINT = "OP_PRINT"
    OP_JUMP = "OP_JUMP"
    OP_JUMP_CONDITIONAL = "OP_JUMP_CONDITIONAL"


operator_mapping: Dict[token_type.TokenType, OpCode] = {
    token_type.TokenType.PLUS: OpCode.OP_ADD,
    token_type.TokenType.MINUS: OpCode.OP_SUBTRACT,
    token_type.TokenType.STAR: OpCode.OP_MULTIPLY,
    token_type.TokenType.SLASH: OpCode.OP_DIVIDE,
    token_type.TokenType.BANG_EQUAL: OpCode.OP_EQUAL,
    token_type.TokenType.EQUAL_EQUAL: OpCode.OP_EQUAL,
    token_type.TokenType.GREATER: OpCode.OP_GREATER,
    token_type.TokenType.GREATER_EQUAL: OpCode.OP_LESS,
    token_type.TokenType.LESS: OpCode.OP_LESS,
    token_type.TokenType.LESS_EQUAL: OpCode.OP_GREATER,
}


@dataclasses.dataclass
class Function:
    """ """

    function_type: FunctionType
    bytecode: List[Byte]
    name: Optional[str]


def init_function(function_type: FunctionType, name: Optional[str] = None) -> Function:
    """ """
    bytecode: List[Byte] = []
    return Function(function_type=function_type, bytecode=bytecode, name=name)


@dataclasses.dataclass
class Local:
    """ """

    name: Optional[token_class.Token]
    depth: int


@dataclasses.dataclass
class Locals:
    """ """

    array: List[Local]
    count: int
    scope_depth: int


def init_locals() -> Locals:
    """ """
    array = [Local(None, 0) for _ in range(INT_COUNT)]
    return Locals(array=array, count=0, scope_depth=0)


@dataclasses.dataclass
class Value:
    """ """

    value: Union[int, Function, None]


@dataclasses.dataclass
class Values:
    """ """

    array: List[Value]
    count: int


def init_values() -> Values:
    """ """
    array: List[Value] = [Value(None) for _ in range(INT_COUNT)]
    return Values(array=array, count=0)


def write(vector: Values, constant: Union[int, Function]) -> Tuple[Values, int]:
    """ """
    vector.array[vector.count] = Value(constant)
    vector.count += 1

    return vector, vector.count - 1


@dataclasses.dataclass
class Compiler:
    """ """

    enclosing: Optional["Compiler"]
    statements: Optional[List[statem.Statem]]
    function: Function
    listing: Locals


def init_compiler(
    composer: Optional["Compiler"] = None,
    statements: Optional[List[statem.Statem]] = None,
    function_type: Optional[FunctionType] = None,
    name: Optional[str] = None,
) -> Compiler:
    """ """
    if function_type is None:
        function_type = FunctionType.TYPE_SCRIPT

    individual_token = token_class.Token(token_type.TokenType.NIL, None, 0, 0)

    listing = init_locals()
    listing.array[listing.count] = Local(individual_token, 0)
    listing.count += 1

    return Compiler(
        enclosing=composer,
        statements=statements,
        function=init_function(function_type=function_type, name=name),
        listing=listing,
    )


def compile(composer: Compiler) -> Tuple[List[Byte], Values]:
    """ """
    vector = init_values()
    assert composer.statements is not None

    for statement in composer.statements:
        composer, vector = execute(composer, vector, statement)

    return composer.function.bytecode, vector


def execute(
    composer: Compiler, vector: Values, statement: statem.Statem
) -> Tuple[Compiler, Values]:
    """ """
    if isinstance(statement, statem.Block):
        return execute_block(composer, vector, statement.statements)

    elif isinstance(statement, statem.Expression):
        composer, vector = evaluate(composer, vector, statement.expression)
        composer.function.bytecode.append(OpCode.OP_POP)

        return composer, vector

    elif isinstance(statement, statem.Function):
        # Encapsulate existing compiler as attribute enclosing of new compiler, representing new
        # function environment.
        composer = init_compiler(
            composer=composer,
            function_type=FunctionType.TYPE_FUNCTION,
            name=statement.name.lexeme,
        )

        # Initialize arguments in function scope.
        composer.listing.scope_depth += 1

        for i, parameter in enumerate(statement.parameters):
            composer.listing.array[composer.listing.count] = Local(
                parameter, composer.listing.scope_depth
            )
            composer.listing.count += 1

        composer.listing.scope_depth -= 1

        # Execute function body with arguments in function scope.
        composer, vector = execute_block(composer, vector, statement.body)

        # Exit back to existing compiler.
        constant = composer.function
        enclosing = composer.enclosing

        # Store function in values.
        vector, location = write(vector, constant)

        assert enclosing is not None
        enclosing.function.bytecode += [OpCode.OP_CONSTANT, location]

        return enclosing, vector

    elif isinstance(statement, statem.If):
        composer, vector = evaluate(composer, vector, statement.condition)

        # Represents body of first emit_jump. First placeholder for location to jump to if true,
        # second placeholder if false.
        composer.function.bytecode.append(OpCode.OP_JUMP_CONDITIONAL)
        composer.function.bytecode.append(0xFF)
        composer.function.bytecode.append(0xFF)
        then_location = len(composer.function.bytecode) - 2

        # The jump instruction peeks on the stack, pop needed to remove the condition result from
        # the stack when the condition is true.
        composer.function.bytecode.append(OpCode.OP_POP)

        composer, vector = execute(composer, vector, statement.then_branch)

        # Represents body of second emit_jump. Placeholder for location to jump to after then branch
        # execution is complete.
        composer.function.bytecode.append(OpCode.OP_JUMP)
        composer.function.bytecode.append(0xFF)
        else_location = len(composer.function.bytecode) - 1

        # Represents body of first patch_jump. Sets the known location of the start of the then
        # branch and the start of the else branch in placeholders of first emit_jump.
        composer.function.bytecode[then_location] = 2
        composer.function.bytecode[then_location + 1] = (
            len(composer.function.bytecode) - then_location - 1
        )

        # Remove the condition result from the stack when the condition is false and jump to the
        # start of the else branch takes place.
        composer.function.bytecode.append(OpCode.OP_POP)

        if statement.else_branch is not None:
            composer, vector = execute(composer, vector, statement.else_branch)

        # Represents body of second patch_jump. Sets the known location of the end of the else
        # branch in placeholders of the second emit_jump.
        composer.function.bytecode[else_location] = (
            len(composer.function.bytecode) - else_location
        )

        return composer, vector

    elif isinstance(statement, statem.Print):
        composer, vector = evaluate(composer, vector, statement.expression)
        composer.function.bytecode.append(OpCode.OP_PRINT)

        return composer, vector

    elif isinstance(statement, statem.Var):
        if statement.initializer is not None:
            composer, vector = evaluate(composer, vector, statement.initializer)
        else:
            composer.function.bytecode += [OpCode.OP_CONSTANT, None]

        composer = add_local(composer, statement.name)

        return composer, vector

    raise Exception


def execute_block(
    composer: Compiler, vector: Values, statements: List[statem.Statem]
) -> Tuple[Compiler, Values]:
    """ """
    # Increase scope depth when entering block.
    composer.listing.scope_depth += 1

    for statement in statements:
        composer, vector = execute(composer, vector, statement)

    # Decrease scope depth when exiting block and remove out of scope variables.
    composer.listing.scope_depth -= 1

    while True:
        local = composer.listing.array[composer.listing.count - 1]
        assert local is not None

        if composer.listing.count == 0 or local.depth <= composer.listing.scope_depth:
            break

        composer.function.bytecode.append(OpCode.OP_POP)
        composer.listing.count -= 1

    return composer, vector


def evaluate(
    composer: Compiler, vector: Values, expression: expr.Expr
) -> Tuple[Compiler, Values]:
    """ """
    if isinstance(expression, expr.Assign):
        composer, vector = evaluate(composer, vector, expression.value)
        location = resolve_local(composer, expression.name)

        if location is not None:
            composer.function.bytecode.append(OpCode.OP_SET)
            composer.function.bytecode.append(location)

            return composer, vector

    elif isinstance(expression, expr.Binary):
        composer, vector = evaluate(composer, vector, expression.left)
        composer, vector = evaluate(composer, vector, expression.right)

        individual_type = expression.operator.token_type

        operator = operator_mapping[individual_type]
        composer.function.bytecode.append(operator)

        if individual_type in [
            token_type.TokenType.BANG_EQUAL,
            token_type.TokenType.GREATER_EQUAL,
            token_type.TokenType.LESS_EQUAL,
        ]:
            composer.function.bytecode.append(OpCode.OP_NOT)

        return composer, vector

    elif isinstance(expression, expr.Grouping):
        return evaluate(composer, vector, expression.expression)

    elif isinstance(expression, expr.Literal):
        vector, location = write(vector, expression.value)
        composer.function.bytecode += [OpCode.OP_CONSTANT, location]

        return composer, vector

    elif isinstance(expression, expr.Unary):
        composer, vector = evaluate(composer, vector, expression.right)
        composer.function.bytecode.append(OpCode.OP_NEGATE)

        return composer, vector

    elif isinstance(expression, expr.Variable):
        location = resolve_local(composer, expression.name)

        if location is not None:
            composer.function.bytecode.append(OpCode.OP_GET)
            composer.function.bytecode.append(location)

            return composer, vector

    raise Exception


def add_local(composer: Compiler, individual_token: token_class.Token) -> Compiler:
    """ """
    composer.listing.array[composer.listing.count] = Local(
        individual_token, composer.listing.scope_depth
    )
    composer.listing.count += 1

    return composer


def resolve_local(
    composer: Compiler, individual_token: token_class.Token
) -> Optional[int]:
    """ """
    for i in range(composer.listing.count - 1, -1, -1):
        local = composer.listing.array[i]
        assert local.name is not None

        if individual_token.lexeme == local.name.lexeme:
            return i

    return None
