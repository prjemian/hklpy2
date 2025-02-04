"""Test the hklpy2.ops module."""

import uuid

import pytest

from ..geom import SimulatedTheta2Theta
from . import models

SKIP_EXACT_VALUE_TEST = str(uuid.uuid4())


@pytest.mark.parametrize(
    "dclass, dname, keypath, value",
    [
        [models.Fourc, "fourc", "_header", SKIP_EXACT_VALUE_TEST],
        [models.Fourc, "fourc", "name", "fourc"],
        [models.Fourc, "fourc", "axes.axes_xref", {}],
        [models.Fourc, "fourc", "geometry", "E4CV"],
        [models.Fourc, "fourc", "solver.name", "hkl_soleil"],
        [models.Fourc, "fourc", "samples", SKIP_EXACT_VALUE_TEST],
        [models.Fourc, "fourc", "solver.version", SKIP_EXACT_VALUE_TEST],
        [SimulatedTheta2Theta, "t2t", "_header", SKIP_EXACT_VALUE_TEST],
        [SimulatedTheta2Theta, "t2t", "name", "t2t"],
        [
            SimulatedTheta2Theta,
            "t2t",
            "axes.axes_xref",
            {"q": "q", "theta": "th", "ttheta": "tth"},
        ],
        [SimulatedTheta2Theta, "t2t", "axes.pseudo_axes", ["q"]],
        [SimulatedTheta2Theta, "t2t", "axes.real_axes", ["theta", "ttheta"]],
        [SimulatedTheta2Theta, "t2t", "geometry", "TH TTH Q"],
        [SimulatedTheta2Theta, "t2t", "solver.name", "th_tth"],
    ],
)
def test_asdict(dclass, dname, keypath, value):
    """."""
    fourc = dclass(name=dname)

    db = fourc.operator._asdict()
    assert db["name"] == dname

    # Walk through the keypath, revising the db object at each step
    for k in keypath.split("."):
        db = db.get(k)  # narrow the search
        assert db is not None, f"{k=!r}"  # Ensure the path exists, so far.

    if value == SKIP_EXACT_VALUE_TEST:
        assert value is not None  # Anything BUT 'None'
    else:
        assert value == db, f"{value=!r}  {db=!r}"
