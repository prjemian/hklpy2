"""Test the hklpy2.ops module."""

import pytest
from ..geom import SimulatedTheta2Theta
from . import models


@pytest.mark.parametrize(
    "dmodel, dname, key, value",
    [
        [models.Fourc, "fourc", "name", "fourc"],
        [models.Fourc, "fourc", "axes_xref", {}],
        [models.Fourc, "fourc", "geometry", "E4CV"],
        [models.Fourc, "fourc", "solver_name", "hkl_soleil"],
        [models.Fourc, "fourc", "samples", None],
        [models.Fourc, "fourc", "solver_version", None],
        [SimulatedTheta2Theta, "t2t", "name", "t2t"],
        [
            SimulatedTheta2Theta,
            "t2t",
            "axes_xref",
            {"q": "q", "theta": "th", "ttheta": "tth"},
        ],
        [SimulatedTheta2Theta, "t2t", "pseudo_axes", ["q"]],
        [SimulatedTheta2Theta, "t2t", "real_axes", ["theta", "ttheta"]],
        [SimulatedTheta2Theta, "t2t", "geometry", "TH TTH Q"],
        [SimulatedTheta2Theta, "t2t", "solver_name", "th_tth"],
    ],
)
def test_asdict(dmodel, dname, key, value):
    fourc = dmodel(name=dname)

    db = fourc.operator._asdict()
    assert key in db, f"{key=!r}  {db=!r}"
    if value is not None:
        assert value == db[key], f"{value=!r}  {db=!r}"
