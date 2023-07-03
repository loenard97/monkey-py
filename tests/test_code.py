from pymonkey.code.code import Encoder, Instructions, MOpcode


def run_test(test_input: dict) -> None:
    for i, (key, value) in enumerate(test_input.items()):
        assert value == Encoder.make(
            key[0], *key[1:]
        ), f"Test {i} failed: {value} != {Encoder.make(key)}"


def assert_instructions_string(test_input: dict) -> None:
    for i, (key, value) in enumerate(test_input.items()):
        instructions = Instructions([])
        for k in key:
            compiled = Encoder.make(k[0], *k[1:])
            instructions.append(compiled)

        assert str(instructions) == value, f"Test {i} failed"


def test_make() -> None:
    test_input = {
        (MOpcode.OpConstant, 0): b"\x01\x00\x00",
        (MOpcode.OpConstant, 65534): b"\x01\xFF\xFE",
        (MOpcode.OpAdd,): b"\x03",
    }

    run_test(test_input)


def test_instructions_string() -> None:
    test_input = {
        (
            (MOpcode.OpConstant, 0),
            (MOpcode.OpConstant, 65534),
            (MOpcode.OpAdd,),
            (MOpcode.OpPop,),
        ): "\
0000 MOpcode.OpConstant 0x00 0x00\n\
0003 MOpcode.OpConstant 0xff 0xfe\n\
0006 MOpcode.OpAdd\n\
0007 MOpcode.OpPop"
    }

    assert_instructions_string(test_input)
