import inspect

import pytest

from ... import SolverError
from ... import get_solver


@pytest.mark.parametrize(
    "solver_name, geometry", [["hkl_soleil", "E4CV"], ["no_op", "anything"]]
)
def test_solvers(solver_name, geometry):
    from importlib.metadata import entry_points

    solvers = entry_points(group="hklpy2.solver")
    assert len(solvers) > 0
    assert solver_name in solvers.names, f"{solver_name=}"

    entrypoint = solvers[solver_name]
    assert entrypoint is not None

    solver_class = entrypoint.load()
    assert inspect.isclass(solver_class)

    solver = solver_class(geometry)
    assert isinstance(solver.version, str)
    assert len(solver.version) > 0, f"{solver.version=}"


def test_HklSolver():
    Solver = get_solver("hkl_soleil")
    assert Solver is not None

    solver = Solver("E4CV")
    assert solver is not None
    assert isinstance(solver.version, str)

    gname = "ESRF ID01 PSIC"
    with pytest.raises(SolverError) as reason:
        solver.geometry = gname
    assert "Geometry E4CV cannot be changed." in str(reason)
    assert solver.geometry is not None
    assert solver.geometry == "E4CV"  # did not change
    assert solver.engine_name == "hkl"

    reals = solver.real_axis_names
    assert reals == "omega chi phi tth".split()

    pseudos = solver.pseudo_axis_names
    assert pseudos == "h k l".split()

    solver = Solver(gname)
    assert solver.geometry == gname  # did not change
    assert solver.engine_name == "hkl"

    reals = solver.real_axis_names
    assert reals == "mu eta phi nu delta".split()

    pseudos = solver.pseudo_axis_names
    assert pseudos == "h k l".split()
