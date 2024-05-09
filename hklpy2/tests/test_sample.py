from contextlib import nullcontext as does_not_raise

import pytest

from .. import Lattice
from .. import ReflectionsDict
from .. import Sample
from .. import SolverBase
from .. import get_solver
from ..misc import unique_name

no_op_solver = get_solver("no_op")()


def test_with_solver_base():
    """Special case that does not fit constructor test."""
    reason = "Can't instantiate abstract class SolverBase"
    with pytest.raises(TypeError) as excuse:
        Sample(SolverBase(), Lattice(4), name="solver")
    assert reason in str(excuse.value), f"{excuse=}"


@pytest.mark.parametrize(
    "solver, lattice, sname, outcome, reason",
    [
        [no_op_solver, Lattice(4), "sample name", does_not_raise(), None],
        [no_op_solver, Lattice(4), None, does_not_raise(), None],
        [
            None,  # <-- not a subclass of SolverBase
            None,
            None,
            pytest.raises(TypeError),
            "Must supply SolverBase() object,",
        ],
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
def test_constructor(solver, lattice, sname, outcome, reason):
    with outcome as excuse:
        sample = Sample(solver, lattice, name=sname)
        assert sample is not None
        if sname is None:
            assert isinstance(sample.name, str)
            assert len(sample.name) == len(unique_name())
        else:
            assert sample.name == sname
        assert isinstance(sample.lattice, Lattice), f"{sample.lattice=}"
        assert isinstance(sample.reflections, ReflectionsDict)

    if reason is not None:
        assert reason in str(excuse.value), f"{excuse=}"
