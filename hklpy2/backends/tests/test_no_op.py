"""Test the no_op solver class."""

# Many features are tested, albeit indrectly, in specific solvers.

# import pyRestTable
# import pytest
# from contextlib import nullcontext as does_not_raise
# context, expected
#     with context as reason:
#         pass
#     assert_context_result(expected, reason)

from ..no_op import NoOpSolver


def test_NoOpSolver():
    assert NoOpSolver.geometries() == []

    solver = NoOpSolver("no_geometry")
    assert solver.removeAllReflections() is None
    assert solver.refineLattice([]) is None
    assert solver.extra_axis_names == []
    assert solver.forward({}) == [{}]
    assert solver.calculate_UB(None, None) == []
    assert solver.addReflection(None) is None
