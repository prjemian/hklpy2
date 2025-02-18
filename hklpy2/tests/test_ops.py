"""Test the hklpy2.ops module."""

import uuid

import pytest

from ..diffract import DiffractometerBase
from ..geom import creator
from ..ops import Operations

SKIP_EXACT_VALUE_TEST = str(uuid.uuid4())


@pytest.mark.parametrize(
    "geometry, solver, name, keypath, value",
    [
        ["E4CV", "hkl_soleil", "fourc", "_header", SKIP_EXACT_VALUE_TEST],
        ["E4CV", "hkl_soleil", "fourc", "_header.datetime", SKIP_EXACT_VALUE_TEST],
        ["E4CV", "hkl_soleil", "fourc", "_header.wavelength", SKIP_EXACT_VALUE_TEST],
        ["E4CV", "hkl_soleil", "fourc", "name", "fourc"],
        ["E4CV", "hkl_soleil", "fourc", "solver.geometry", "E4CV"],
        ["E4CV", "hkl_soleil", "fourc", "solver.name", "hkl_soleil"],
        ["E4CV", "hkl_soleil", "fourc", "samples", SKIP_EXACT_VALUE_TEST],
        ["E4CV", "hkl_soleil", "fourc", "solver.version", SKIP_EXACT_VALUE_TEST],
        #
        ["TH TTH Q", "th_tth", "t2t", "_header", SKIP_EXACT_VALUE_TEST],
        ["TH TTH Q", "th_tth", "t2t", "_header.datetime", SKIP_EXACT_VALUE_TEST],
        ["TH TTH Q", "th_tth", "t2t", "_header.wavelength", SKIP_EXACT_VALUE_TEST],
        ["TH TTH Q", "th_tth", "t2t", "name", "t2t"],
        [
            "TH TTH Q",
            "th_tth",
            "t2t",
            "axes.axes_xref",
            {"q": "q", "th": "th", "tth": "tth"},
        ],
        ["TH TTH Q", "th_tth", "t2t", "axes.pseudo_axes", ["q"]],
        ["TH TTH Q", "th_tth", "t2t", "axes.real_axes", ["th", "tth"]],
        ["TH TTH Q", "th_tth", "t2t", "solver.geometry", "TH TTH Q"],
        ["TH TTH Q", "th_tth", "t2t", "solver.name", "th_tth"],
    ],
)
def test_asdict(geometry, solver, name, keypath, value):
    """."""
    diffractometer = creator(name=name, geometry=geometry, solver=solver)
    assert isinstance(
        diffractometer, DiffractometerBase
    ), f"{geometry=} {solver=} {name=}"
    assert isinstance(
        diffractometer.operator, Operations
    ), f"{geometry=} {solver=} {name=}"

    db = diffractometer.operator._asdict()
    assert db["name"] == name

    # Walk through the keypath, revising the db object at each step
    for k in keypath.split("."):
        db = db.get(k)  # narrow the search
        assert db is not None, f"{k=!r}"  # Ensure the path exists, so far.

    if value == SKIP_EXACT_VALUE_TEST:
        assert value is not None  # Anything BUT 'None'
    else:
        assert value == db, f"{value=!r}  {db=!r}"
