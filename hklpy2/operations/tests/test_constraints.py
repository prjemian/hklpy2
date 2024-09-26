import pytest

from ..constraints import ConstraintBase
from ..constraints import ConstraintsError
from ..constraints import LimitsConstraint
from ..constraints import RealAxisConstraints


def test_raises():
    with pytest.raises(TypeError) as excuse:
        ConstraintBase()
    assert "Can't instantiate abstract class" in str(excuse)

    with pytest.raises(ConstraintsError) as excuse:
        LimitsConstraint(0, 1)
    assert "Must provide a value" in str(excuse)

    c = LimitsConstraint(0, 1, label="test")
    with pytest.raises(ConstraintsError) as excuse:
        c.valid()
    assert "did not include this constraint" in str(excuse)


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
    c = LimitsConstraint(lo, hi, label="axis")
    assert len(c._asdict()) == 4

    text = str(c)
    assert " <= " in text

    assert c.low_limit == lo or -180, f"{c!r}"
    assert c.high_limit == hi or 180, f"{c!r}"
    assert c.valid(axis=value) == result, f"{c!r}"


@pytest.mark.parametrize(
    "reals, result",
    [
        [{"aa": 0, "bb": 0, "cc": 0}, True],
        [{"aa": 0, "bb": 200, "cc": 0}, False],
    ],
)
def test_RealAxisConstraints(reals, result):
    ac = RealAxisConstraints(list(reals))
    assert len(ac) == len(reals)
    assert len(ac._asdict()) == len(reals), f"{ac._asdict()!r}"
    assert ac.valid(**reals) == result


def test_RealAxisConstraintsKeys():
    ac = RealAxisConstraints("tinker evers chance".split())
    with pytest.raises(ConstraintsError) as excuse:
        ac.valid(you=0, me=0)
    assert "did not include this constraint" in str(excuse)


def test_fromdict():
    config = {
        "class": "LimitsConstraint",
        "high_limit": 120.0,
        "label": "chi",
        "low_limit": -5.0,
    }
    c = LimitsConstraint(label=config["label"])
    assert c.label == config["label"]
    assert c.low_limit != config["low_limit"]
    assert c.high_limit != config["high_limit"]

    c._fromdict(config)
    assert c.label == config["label"]
    assert c.low_limit == config["low_limit"]
    assert c.high_limit == config["high_limit"]

    config = {
        "chi": {
            "class": "LimitsConstraint",
            "high_limit": 120.0,
            "label": "chi",
            "low_limit": -5.0,
        },
        "phi": {
            "class": "LimitsConstraint",
            "high_limit": 85.0,
            "label": "phi",
            "low_limit": 30.0,
        },
    }
    ac = RealAxisConstraints(list(config))
    assert len(ac) == len(config)
    assert "chi" in ac
    assert ac["chi"].low_limit == -180.0
    assert ac["chi"].high_limit == 180.0
    assert "phi" in ac
    assert ac["phi"].low_limit == -180.0
    assert ac["phi"].high_limit == 180.0

    ac._fromdict(config)
    assert ac["chi"].low_limit == -5.0
    assert ac["chi"].high_limit == 120.0
    assert ac["phi"].low_limit == 30.0
    assert ac["phi"].high_limit == 85.0

    # TODO: Also test for exceptions.
