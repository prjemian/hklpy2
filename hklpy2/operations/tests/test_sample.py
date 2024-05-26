from contextlib import nullcontext as does_not_raise

import pytest

from ..lattice import Lattice
from ..sample import Sample
from ..reflection import ReflectionsDict
from ..misc import unique_name


def test_sample_constructor_no_operator():
    with pytest.raises(TypeError) as reason:
        Sample(None, "test", Lattice(4))
    assert "expected SolverOperator" in str(reason), f"{reason=!r}"


@pytest.mark.parametrize(
    "lattice, sname, outcome, expect",
    [
        [Lattice(4), "sample name", does_not_raise(), None],
        [Lattice(4), None, does_not_raise(), None],
        [None, None, pytest.raises(TypeError), "Must supply Lattice"],
        [
            None,  # <-- not a Lattice
            None,
            pytest.raises(TypeError),
            "Must supply Lattice() object,",
        ],
        [
            (1, 2),  # <-- not a Lattice
            None,
            pytest.raises(TypeError),
            "Must supply Lattice() object,",
        ],
        [
            dict(a=1, b=2, c=3, alpha=4, beta=5, gamma=6),  # <-- not a Lattice
            None,
            pytest.raises(TypeError),
            "Must supply Lattice() object,",
        ],
        [
            Lattice(4),
            12345,  # <-- not a str
            pytest.raises(TypeError),
            "Must supply str,",
        ],
    ],
)
def test_sample_constructor(lattice, sname, outcome, expect, sim):
    with outcome as excuse:
        sample = Sample(sim.operator, sname, lattice)
        assert sample is not None

        if sname is None:
            assert isinstance(sample.name, str)
            assert len(sample.name) == len(unique_name())
        else:
            assert sample.name == sname
        assert isinstance(sample.lattice, Lattice), f"{sample.lattice=}"
        assert isinstance(sample.reflections, ReflectionsDict)

    if expect is not None:
        assert expect in str(excuse), f"{excuse=} {expect=}"


def test_repr(sim):
    rep = repr(sim.sample)
    assert rep.startswith("Sample(")
    assert "name=" in rep
    assert "lattice=" in rep
    assert rep.endswith(")")


def test_reflections_fail(sim):
    with pytest.raises(TypeError) as reason:
        sim.sample.reflections = None
    assert "Must supply ReflectionsDict" in str(reason)
