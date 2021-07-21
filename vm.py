from typing import List, Optional, Tuple
import dataclasses

import compiler


STACK_MAX = 8


@dataclasses.dataclass
class VM:
    """ """

    bytecode: List[compiler.ByteCode]
    ip: int = 0
    stack: Optional[List[Optional[int]]] = None
    top: int = 0


def init_vm(bytecode: List[compiler.ByteCode]) -> VM:
    """ """
    emulator = VM(bytecode=bytecode)
    emulator.stack = [None] * STACK_MAX

    return emulator


def push(emulator: VM, value: int) -> VM:
    """ """
    assert emulator.stack is not None
    emulator.stack[emulator.top] = value
    emulator.top += 1

    return emulator


def pop(emulator: VM) -> Tuple[VM, int]:
    """ """
    emulator.top -= 1
    assert emulator.stack is not None
    value = emulator.stack[emulator.top]

    assert value is not None
    return emulator, value


def read_byte(emulator: VM) -> Tuple[VM, compiler.ByteCode]:
    """ """
    emulator.ip += 1
    instruction = emulator.bytecode[emulator.ip - 1]

    return emulator, instruction


def read_constant(emulator: VM) -> Tuple[VM, int]:
    """ """
    emulator, constant = read_byte(emulator)

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


def run(emulator: VM) -> int:
    """ """
    while not is_at_end(emulator):
        emulator, instruction = read_byte(emulator)

        if instruction == compiler.OpCode.OP_CONSTANT:
            emulator, constant = read_constant(emulator)
            emulator = push(emulator, constant)

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
            constant = -constant
            emulator = push(emulator, constant)

    assert emulator.top == 1
    assert emulator.stack is not None
    result = emulator.stack[0]

    assert result is not None
    return result
