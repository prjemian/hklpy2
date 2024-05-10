from ... import get_solver
from .. import SolverBase
from ..th_tth_q import ThTthSolver


def test_solver():
    assert issubclass(ThTthSolver, SolverBase)
    assert get_solver("th_tth") == ThTthSolver

    solver = ThTthSolver()
    assert isinstance(solver, SolverBase)
    assert solver.__name__ == "th_tth"
    assert solver.geometries == ["TH TTH Q"]

    assert solver.geometry is None
    assert solver.pseudo_axis_names == []
    assert solver.real_axis_names == []

    solver.geometry = "TH TTH Q"
    assert solver.geometry == "TH TTH Q"
    assert solver.pseudo_axis_names == ["q"]
    assert solver.real_axis_names == "th tth".split()

    assert solver.mode is None
    solver.mode = "bisector"
    assert solver.mode == "bisector"

    solver.wavelength = 1.0
    result = solver.inverse({"tth": 10.0})
    assert isinstance(result, dict)
    assert "q" in result
    assert round(result["q"], 4) == 1.0952, f"{result=!r}"

    result = solver.forward(result)
    assert isinstance(result, list)
    assert len(result) == 1

    result = result[0]
    assert isinstance(result, dict)
    assert "th" in result
    assert "tth" in result
    assert round(result["th"], 4) == 5, f"{result=!r}"
    assert round(result["tth"], 4) == 10, f"{result=!r}"
