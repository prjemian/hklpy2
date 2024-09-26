import pytest

from ..misc import roundoff


@pytest.mark.parametrize(
    "value, digits, expected_text",
    [
        [0, None, "0"],
        [0.123456, None, "0"],
        [0.123456, 4, "0.1235"],
        [-0, 4, "0"],
        [123456, 4, "123456"],
        [123456, -4, "120000"],
        [1.23456e-10, 4, "0"],
        [1.23456e-10, 12, "1.23e-10"],
    ]
)
def test_roundoff(value, digits, expected_text):
    result = roundoff(value, digits)
    assert str(result) == expected_text
