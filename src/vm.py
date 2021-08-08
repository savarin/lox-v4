from typing import List, Optional, Tuple
import dataclasses

import compiler
import helpers


STACK_MAX = 16


@dataclasses.dataclass
class VM:
    """ """

    bytecode: List[compiler.Byte]
    values: compiler.Values
    ip: int
    stack: Optional[List[Optional[int]]]
    top: int


def init_vm(bytecode: List[compiler.Byte], values: compiler.Values) -> VM:
    """ """
    return VM(bytecode=bytecode, values=values, ip=0, stack=[None] * STACK_MAX, top=0)


def push(emulator: VM, value: Optional[int]) -> VM:
    """ """
    assert emulator.stack is not None
    emulator.stack[emulator.top] = value
    emulator.top += 1

    return emulator


def pop(emulator: VM) -> Tuple[VM, Optional[int]]:
    """ """
    assert emulator.stack is not None
    emulator.top -= 1

    value = emulator.stack[emulator.top]

    return emulator, value


def shift(emulator: VM, position: int) -> Optional[int]:
    """ """
    offset = emulator.bytecode[emulator.ip + position]
    assert isinstance(offset, int)

    # Ensure shift by offset amount not exceed length of bytecode.
    if emulator.ip + offset >= len(emulator.bytecode):
        return None

    return offset


def read_byte(emulator: VM) -> Tuple[VM, compiler.Byte]:
    """ """
    emulator.ip += 1
    instruction = emulator.bytecode[emulator.ip - 1]

    return emulator, instruction


def read_constant(emulator: VM) -> Tuple[VM, Optional[int]]:
    """ """
    emulator, location = read_byte(emulator)

    if location is None:
        return emulator, None

    assert isinstance(location, int)
    constant = emulator.values.array[location].value

    assert isinstance(constant, int)
    return emulator, constant


def binary_op(emulator: VM, op: str) -> VM:
    """ """
    emulator, b = pop(emulator)
    emulator, a = pop(emulator)

    return push(emulator, eval(f"a {op} b"))


def is_at_end(emulator: VM) -> bool:
    """ """
    return emulator.ip == len(emulator.bytecode)


def run(emulator: VM) -> List[helpers.Result]:
    """ """
    result: List[helpers.Result] = []

    while not is_at_end(emulator):
        emulator, instruction = read_byte(emulator)

        if instruction == compiler.OpCode.OP_CONSTANT:
            emulator, constant = read_constant(emulator)
            emulator = push(emulator, constant)

        elif instruction == compiler.OpCode.OP_POP:
            emulator, constant = pop(emulator)
            result.append(constant)

        elif instruction == compiler.OpCode.OP_GET:
            emulator, location = read_byte(emulator)

            assert emulator.stack is not None
            assert isinstance(location, int)
            value = emulator.stack[location]
            emulator = push(emulator, value)
            result.append(None)

        elif instruction == compiler.OpCode.OP_SET:
            emulator, location = read_byte(emulator)

            assert emulator.stack is not None
            assert isinstance(location, int)
            value = emulator.stack[emulator.top - 1]
            emulator.stack[location] = value
            result.append(None)

        elif instruction == compiler.OpCode.OP_EQUAL:
            emulator, b = pop(emulator)
            emulator, a = pop(emulator)

            emulator = push(emulator, helpers.is_equal(a, b))

        elif instruction == compiler.OpCode.OP_GREATER:
            emulator = binary_op(emulator, ">")

        elif instruction == compiler.OpCode.OP_LESS:
            emulator = binary_op(emulator, "<")

        elif instruction == compiler.OpCode.OP_ADD:
            emulator = binary_op(emulator, "+")

        elif instruction == compiler.OpCode.OP_SUBTRACT:
            emulator = binary_op(emulator, "-")

        elif instruction == compiler.OpCode.OP_MULTIPLY:
            emulator = binary_op(emulator, "*")

        elif instruction == compiler.OpCode.OP_DIVIDE:
            emulator = binary_op(emulator, "//")

        elif instruction == compiler.OpCode.OP_NOT:
            emulator, constant = pop(emulator)
            emulator = push(emulator, not helpers.is_truthy(constant))

        elif instruction == compiler.OpCode.OP_NEGATE:
            emulator, constant = pop(emulator)

            assert constant is not None
            constant = -constant
            emulator = push(emulator, -constant)

        elif instruction == compiler.OpCode.OP_PRINT:
            emulator, individual_result = pop(emulator)
            result.append(
                str(individual_result if individual_result is not None else "nil")
            )

        elif instruction == compiler.OpCode.OP_JUMP:
            offset = shift(emulator, 0)

            if offset is None:
                break

            emulator.ip += offset

        elif instruction == compiler.OpCode.OP_JUMP_CONDITIONAL:
            assert emulator.stack is not None
            condition = emulator.stack[emulator.top - 1]

            if helpers.is_truthy(condition):
                offset = shift(emulator, 0)
            else:
                offset = shift(emulator, 1)

            if offset is None:
                break

            emulator.ip += offset

    return result
