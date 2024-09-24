"""Test the hklpy2.ops module."""

import pytest

from ..geom import SimulatedTheta2Theta
from . import models


@pytest.mark.parametrize(
    "dclass, dname, keypath, value",
    [
        [models.Fourc, "fourc", "name", "fourc"],
        [models.Fourc, "fourc", "axes.axes_xref", {}],
        [models.Fourc, "fourc", "geometry", "E4CV"],
        [models.Fourc, "fourc", "solver.name", "hkl_soleil"],
        [models.Fourc, "fourc", "samples", None],
        [models.Fourc, "fourc", "solver.version", None],
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
    fourc = dclass(name=dname)

    db = fourc.operator._asdict()
    assert db["name"] == dname
    assert "_header" not in db  # _header is add by 'configure' module

    for k in keypath.split("."):
        db = db.get(k)  # narrow the search
        assert db is not None, f"{k=!r}"

    if value is not None:
        assert value == db, f"{value=!r}  {db=!r}"
