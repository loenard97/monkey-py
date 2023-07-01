from typing import Dict

from pymonkey.code.code import Encoder, MOpcode


def run_test(test_input: Dict):
    for i, (key, value) in enumerate(test_input.items()):
        assert value == Encoder.make(
            key[0], *key[1:]
        ), f"Test {i} failed: {value} != {Encoder.make(key)}"


def test_make():
    test_input = {
        (MOpcode.OpConstant, 0): b"\x01\x00\x00",
        (MOpcode.OpConstant, 65534): b"\x01\xFF\xFE",
    }

    run_test(test_input)
