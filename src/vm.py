from typing import List, Optional, Tuple, Union
import dataclasses

import compiler
import helpers


FRAMES_MAX = 8
STACK_MAX = 8


@dataclasses.dataclass
class CallFrame:
    """ """

    function: Optional[compiler.Function]
    ip: int
    slots: Optional[List[Union[int, compiler.Function, None]]]
    slots_top: int


@dataclasses.dataclass
class VM:
    """ """

    frames: List[CallFrame]
    frame_count: int
    stack: List[Union[int, compiler.Function, None]]
    stack_top: int


def init_vm(function: compiler.Function) -> VM:
    """ """
    frames = [CallFrame(None, 0, None, 0) for _ in range(FRAMES_MAX)]

    stack: List[Union[int, compiler.Function, None]] = [None] * STACK_MAX
    stack[0] = function

    return VM(frames=frames, frame_count=0, stack=stack, stack_top=1)


def call(
    emulator: VM,
    frame: Optional[CallFrame],
    function: compiler.Function,
    arg_count: int,
) -> Tuple[VM, Optional[CallFrame], bool]:
    """ """
    if emulator.frame_count > STACK_MAX:
        return emulator, frame, False

    if frame is None:
        slots: List[Union[int, compiler.Function, None]] = [None] * STACK_MAX
    else:
        assert frame.slots is not None
        slots = frame.slots[frame.slots_top - arg_count - 1 :]

    frame = CallFrame(function=function, ip=0, slots=slots, slots_top=arg_count + 1)

    emulator.frames[emulator.frame_count] = frame
    emulator.frame_count += 1

    return emulator, frame, True


def push(frame: CallFrame, value: Union[int, compiler.Function, None]) -> CallFrame:
    """ """
    assert frame.slots is not None
    frame.slots[frame.slots_top] = value
    frame.slots_top += 1

    return frame


def pop(frame: CallFrame) -> Tuple[CallFrame, Union[int, compiler.Function, None]]:
    """ """
    frame.slots_top -= 1

    assert frame.slots is not None
    value = frame.slots[frame.slots_top]

    return frame, value


def shift(frame: CallFrame, position: int) -> Optional[int]:
    """ """
    assert frame.function is not None
    offset = frame.function.bytecode[frame.ip + position]

    assert isinstance(offset, int)

    # Ensure shift by offset amount not exceed length of bytecode.
    if frame.ip + offset >= len(frame.function.bytecode):
        return None

    return offset


def read_byte(frame: CallFrame) -> Tuple[CallFrame, compiler.Byte]:
    """ """
    frame.ip += 1

    assert frame.function is not None
    instruction = frame.function.bytecode[frame.ip - 1]

    return frame, instruction


def read_constant(
    frame: CallFrame,
) -> Tuple[CallFrame, Union[int, compiler.Function, None]]:
    """ """
    frame, location = read_byte(frame)

    if location is None:
        return frame, None

    assert frame.function is not None
    assert frame.function.values is not None
    assert isinstance(location, int)
    constant = frame.function.values.array[location].value

    return frame, constant


def binary_op(frame: CallFrame, op: str) -> CallFrame:
    """ """
    frame, b = pop(frame)
    frame, a = pop(frame)

    return push(frame, eval(f"a {op} b"))


def is_at_end(frame: CallFrame) -> bool:
    """ """
    assert frame.function is not None
    return frame.ip >= len(frame.function.bytecode)


def run(emulator: VM) -> List[helpers.Result]:
    """ """
    result: List[helpers.Result] = []

    function = emulator.stack[emulator.stack_top - 1]

    assert isinstance(function, compiler.Function)
    emulator, frame, is_valid = call(emulator, None, function, 0)

    if not is_valid:
        return result

    while True:
        assert frame is not None

        if is_at_end(frame):
            break

        frame, instruction = read_byte(frame)

        if instruction == compiler.OpCode.OP_CONSTANT:
            frame, constant_value = read_constant(frame)
            frame = push(frame, constant_value)

        elif instruction == compiler.OpCode.OP_POP:
            frame, pop_value = pop(frame)

            assert isinstance(pop_value, int)
            result.append(pop_value)

        elif instruction == compiler.OpCode.OP_GET:
            frame, get_value = read_byte(frame)

            assert frame.slots is not None
            assert isinstance(get_value, int)
            value = frame.slots[get_value]

            frame = push(frame, value)
            result.append(None)

        elif instruction == compiler.OpCode.OP_SET:
            frame, set_value = read_byte(frame)

            assert frame.slots is not None
            value = frame.slots[frame.slots_top - 1]

            assert isinstance(set_value, int)
            frame.slots[set_value] = value
            result.append(None)

        elif instruction == compiler.OpCode.OP_EQUAL:
            frame, b = pop(frame)
            frame, a = pop(frame)

            assert isinstance(a, int) and isinstance(b, int)
            frame = push(frame, helpers.is_equal(a, b))

        elif instruction == compiler.OpCode.OP_GREATER:
            frame = binary_op(frame, ">")

        elif instruction == compiler.OpCode.OP_LESS:
            frame = binary_op(frame, "<")

        elif instruction == compiler.OpCode.OP_ADD:
            frame = binary_op(frame, "+")

        elif instruction == compiler.OpCode.OP_SUBTRACT:
            frame = binary_op(frame, "-")

        elif instruction == compiler.OpCode.OP_MULTIPLY:
            frame = binary_op(frame, "*")

        elif instruction == compiler.OpCode.OP_DIVIDE:
            frame = binary_op(frame, "//")

        elif instruction == compiler.OpCode.OP_NOT:
            frame, not_value = pop(frame)

            assert not isinstance(not_value, compiler.Function)
            frame = push(frame, not helpers.is_truthy(not_value))

        elif instruction == compiler.OpCode.OP_NEGATE:
            frame, negate_value = pop(frame)

            assert isinstance(negate_value, int)
            negate_value = -negate_value
            frame = push(frame, -negate_value)

        elif instruction == compiler.OpCode.OP_JUMP:
            offset = shift(frame, 0)

            if offset is None:
                break

            frame.ip += offset

        elif instruction == compiler.OpCode.OP_JUMP_CONDITIONAL:
            assert frame.slots is not None
            condition = frame.slots[frame.slots_top - 1]

            assert isinstance(condition, bool)

            if helpers.is_truthy(condition):
                offset = shift(frame, 0)
            else:
                offset = shift(frame, 1)

            if offset is None:
                break

            frame.ip += offset

        elif instruction == compiler.OpCode.OP_CALL:
            frame, call_value = read_byte(frame)

            assert frame.slots is not None
            assert isinstance(call_value, int)
            function = frame.slots[frame.slots_top - 1 - call_value]

            assert isinstance(function, compiler.Function)
            emulator, frame, is_valid = call(emulator, frame, function, call_value)

        elif instruction == compiler.OpCode.OP_PRINT:
            frame, print_value = pop(frame)
            result.append(str(print_value if print_value is not None else "nil"))

    return result
