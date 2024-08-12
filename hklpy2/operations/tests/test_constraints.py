from contextlib import nullcontext as does_not_raise
import pytest

from ..constraints import ConstraintBase, LimitsConstraint, AxisConstraints


def test_ConstraintBase():
    with pytest.raises(TypeError) as excuse:
        ConstraintBase()
    assert "Can't instantiate abstract class" in str(excuse)


@pytest.mark.parametrize(
    "lo, hi, value, result",
    [
        [None, None, 0, True],
        [None, None, 2000, False],
        [0, None, 0, True],
        [0, None, -1, False],
        [10, 20, 0, False],
        [10, 20, 15, True],
        [20, 10, 10, True],
        [20, 10, 15, True],
        [20, 10, 20, True],
    ],
)
def test_LimitsConstraint(lo, hi, value, result):
    c = LimitsConstraint(lo, hi)
    assert len(c._asdict()) == 2

    text = repr(c)
    assert text.startswith("LimitsConstraint(")

    assert c.low_limit == lo or -180, f"{c!r}"
    assert c.high_limit == hi or 180, f"{c!r}"
    assert c.valid(value) == result, f"{c!r}"


@pytest.mark.parametrize(
    "reals, result",
    [
        [{"aa": 0, "bb": 0, "cc": 0}, True],
        [{"aa": 0, "bb": 200, "cc": 0}, False],
    ],
)
def test_AxisConstraints(reals, result):
    ac = AxisConstraints(list(reals.keys()))
    assert len(ac.axes) == len(reals)
    assert len(ac._asdict()) == len(reals), f"{ac._asdict()!r}"
    assert ac.valid(**reals) == result


def test_AxisConstraintsKeys():
    ac = AxisConstraints("tinker evers chance".split())
    with pytest.raises(KeyError) as excuse:
        ac.valid(you=0, me=0)
    assert "Must use the same keys" in str(excuse)
