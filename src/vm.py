from typing import List, Optional, Tuple, Union
import dataclasses

import compiler


Result = Union[int, str, None]


STACK_MAX = 8


@dataclasses.dataclass
class VM:
    """ """

    bytecode: List[compiler.Byte]
    values: compiler.Values
    ip: int = 0
    stack: Optional[List[Optional[int]]] = None
    top: int = 0


def init_vm(bytecode: List[compiler.Byte], values: compiler.Values) -> VM:
    """ """
    return VM(bytecode=bytecode, values=values, stack=[None] * STACK_MAX)


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


def run(emulator: VM) -> List[Result]:
    """ """
    result: List[Result] = []

    while not is_at_end(emulator):
        emulator, instruction = read_byte(emulator)

        if instruction == compiler.OpCode.OP_CONSTANT:
            emulator, constant = read_constant(emulator)
            emulator = push(emulator, constant)

        elif instruction == compiler.OpCode.OP_POP:
            emulator, constant = pop(emulator)
            result.append(constant)

        elif instruction == compiler.OpCode.OP_GET:
            emulator, offset = read_byte(emulator)

            assert emulator.stack is not None
            assert isinstance(offset, int)
            value = emulator.stack[offset]
            emulator = push(emulator, value)
            result.append(None)

        elif instruction == compiler.OpCode.OP_SET:
            emulator, offset = read_byte(emulator)

            assert emulator.stack is not None
            assert isinstance(offset, int)
            value = emulator.stack[emulator.top - 1]
            emulator.stack[offset] = value
            result.append(None)

        elif instruction == compiler.OpCode.OP_ADD:
            emulator = binary_op(emulator, "+")

        elif instruction == compiler.OpCode.OP_SUBTRACT:
            emulator = binary_op(emulator, "-")

        elif instruction == compiler.OpCode.OP_MULTIPLY:
            emulator = binary_op(emulator, "*")

        elif instruction == compiler.OpCode.OP_DIVIDE:
            emulator = binary_op(emulator, "//")

        elif instruction == compiler.OpCode.OP_NEGATE:
            emulator, constant = pop(emulator)

            assert constant is not None
            constant = -constant
            emulator = push(emulator, constant)

        elif instruction == compiler.OpCode.OP_PRINT:
            emulator, individual_result = pop(emulator)
            result.append(str(individual_result or "nil"))

    return result
