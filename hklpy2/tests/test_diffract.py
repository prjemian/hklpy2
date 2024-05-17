"""Test the hklpy2.diffract module."""

import math

import pytest
from ophyd import Component as Cpt
from ophyd import Kind
from ophyd import PseudoSingle
from ophyd import SoftPositioner

from .. import A_KEV
from ..diffract import DEFAULT_PHOTON_ENERGY_KEV
from ..diffract import DiffractometerBase

NORMAL_HINTED = Kind.hinted | Kind.normal


class Fourc(DiffractometerBase):
    h = Cpt(PseudoSingle, "", kind=NORMAL_HINTED)
    k = Cpt(PseudoSingle, "", kind=NORMAL_HINTED)
    l = Cpt(PseudoSingle, "", kind=NORMAL_HINTED)

    omega = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=NORMAL_HINTED)
    chi = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=NORMAL_HINTED)
    phi = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=NORMAL_HINTED)
    tth = Cpt(SoftPositioner, limits=(-170, 170), init_pos=0, kind=NORMAL_HINTED)


class Th2Th(DiffractometerBase):
    q = Cpt(PseudoSingle, "", kind=NORMAL_HINTED)

    th = Cpt(SoftPositioner, limits=(-90, 90), init_pos=0, kind=NORMAL_HINTED)
    tth = Cpt(SoftPositioner, limits=(-170, 170), init_pos=0, kind=NORMAL_HINTED)


def test_DiffractometerBase():
    # TODO: Until more of the baae class is developed, an exception
    # will be raised if an object is created.  Test that situation.
    with pytest.raises(ValueError) as reason:
        DiffractometerBase("", name="dbase")
    assert "Must have at least 1 positioner and pseudo-positioner" in str(reason)


@pytest.mark.parametrize("geometry, npseudos, nreals", [[Fourc, 3, 4], [Th2Th, 1, 2]])
def test_goniometer(geometry, npseudos, nreals):
    goniometer = geometry("", name="goniometer")
    assert goniometer is not None
    assert len(goniometer.pseudo_positioners) == npseudos
    assert len(goniometer._pseudo) == npseudos
    assert len(goniometer.real_positioners) == nreals
    assert len(goniometer._real) == nreals
    assert not goniometer.moving
    assert math.isclose(goniometer.energy.get(), DEFAULT_PHOTON_ENERGY_KEV, abs_tol=0.01)
    assert math.isclose(goniometer.wavelength.get(), A_KEV / DEFAULT_PHOTON_ENERGY_KEV, abs_tol=0.001)
    assert goniometer.solver.get() is None

    # TODO: position needs a solver
    # assert goniometer.position == position, f"{goniometer.position=!r}"
    with pytest.raises(NotImplementedError) as reason:
        goniometer.position
    assert "NotImplementedError" in str(reason), f"{reason=!r}"
    # assert False, f"{goniometer.report}"  # calls .position
