from contextlib import nullcontext as does_not_raise

import pytest

from .. import Lattice
from .. import ReflectionsDict
from .. import Sample
from .. import SolverBase
from .. import solver_factory
from ..misc import unique_name

no_op_solver = solver_factory("no_op", "")


def test_with_solver_base():
    """Special case that does not fit constructor test."""
    reason = "Can't instantiate abstract class SolverBase"
    with pytest.raises(TypeError) as excuse:
        Sample("solver", Lattice(4), SolverBase())
    assert reason in str(excuse.value), f"{excuse=}"


@pytest.mark.parametrize(
    "solver, lattice, sname, outcome, expect",
    [
        [no_op_solver, Lattice(4), "sample name", does_not_raise(), None],
        [no_op_solver, Lattice(4), None, does_not_raise(), None],
        [None, None, None, pytest.raises(TypeError), "Must supply Lattice"],
        [
            no_op_solver,
            None,  # <-- not a Lattice
            None,
            pytest.raises(TypeError),
            "Must supply Lattice() object,",
        ],
        [
            no_op_solver,
            (1, 2),  # <-- not a Lattice
            None,
            pytest.raises(TypeError),
            "Must supply Lattice() object,",
        ],
        [
            no_op_solver,
            dict(a=1, b=2, c=3, alpha=4, beta=5, gamma=6),  # <-- not a Lattice
            None,
            pytest.raises(TypeError),
            "Must supply Lattice() object,",
        ],
        [
            no_op_solver,
            Lattice(4),
            12345,  # <-- not a str
            pytest.raises(TypeError),
            "Must supply str,",
        ],
    ],
)
def test_constructor(solver, lattice, sname, outcome, expect):
    with outcome as excuse:
        sample = Sample(sname, lattice, solver)
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
