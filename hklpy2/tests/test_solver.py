import inspect
from importlib.metadata import entry_points

import pytest


@pytest.mark.parametrize("solver_name", ["hkl_soleil", "no_op"])
def test_solvers(solver_name):
    solvers = entry_points(group="hklpy2.solver")
    assert len(solvers) > 0
    assert solver_name in solvers.names, f"{solver_name=}"

    entrypoint = solvers[solver_name]
    assert entrypoint is not None

    solver_class = entrypoint.load()
    assert inspect.isclass(solver_class)

    solver = solver_class()
    assert isinstance(solver.__version__, str)
    assert len(solver.__version__) > 0, f"{solver.__version__=}"
