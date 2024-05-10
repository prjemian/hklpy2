import numpy as np
import pytest

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


@pytest.mark.parametrize(
    "transform, wavelength, inputs, outputs, tol",
    [
        ["inverse", 0.5, {"th": 60, "tth": 120}, {"q": 21.7655924}, 0.0001],
        ["forward", 0.5, {"q": 21.7655924}, {"th": 60, "tth": 120}, 0.0001],
        ["inverse", 1.0, {"th": 5, "tth": 10}, {"q": 1.095231}, 0.0001],
        ["forward", 1.0, {"q": 1.095231}, {"th": 5, "tth": 10}, 0.0001],
        ["inverse", 1.54, {"th": 14.9131, "tth": 29.8262}, {"q": 2.1}, 0.0001],
        ["forward", 1.54, {"q": 2.1}, {"th": 14.9131, "tth": 29.8262}, 0.0001],
        ["inverse", 2.1, {"th": 1, "tth": 2}, {"q": 0.104435}, 0.0001],
        ["forward", 2.1, {"q": 0.104435}, {"th": 1, "tth": 2}, 0.0001],
        ["inverse", 2.1, {"th": 0.1, "tth": 0.2}, {"q": 0.0104440}, 0.0001],
        ["forward", 2.1, {"q": 0.0104440}, {"th": 0.1, "tth": 0.2}, 0.0001],
        ["inverse", 2.1, {"th": 0.01, "tth": 0.02}, {"q": 0.00104440}, 0.0001],
        ["forward", 2.1, {"q": 0.00104440}, {"th": 0.01, "tth": 0.02}, 0.0001],
    ],
)
def test_transforms(transform, wavelength, inputs, outputs, tol):
    solver = get_solver("th_tth")()
    solver.geometry = "TH TTH Q"
    solver.mode = "bisector"
    solver.wavelength = wavelength
    if transform == "forward":
        result = solver.forward(inputs)
        assert isinstance(result, list)
        assert len(result) == 1
        result = result[0]
        assert "th" in result
        assert "tth" in result
    elif transform == "inverse":
        result = solver.inverse(inputs)
        assert "q" in result
    assert isinstance(result, dict)
    assert list(result.keys()) == list(outputs.keys())
    arr_r = np.array(list(result.values()))
    arr_o = np.array(list(outputs.values()))
    assert np.allclose(arr_r, arr_o, atol=tol), f"{result=}  {outputs=}"
