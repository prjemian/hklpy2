"""Test the hklpy2.diffract module."""

import math

import pytest
from ophyd import Component as Cpt
from ophyd import Kind
from ophyd import PseudoSingle
from ophyd import SoftPositioner

from ..diffract import DiffractometerBase
from ..diffract import DiffractometerError

# from ..misc import get_solver
# from ..misc import solver_factory
from ..wavelength_support import DEFAULT_WAVELENGTH
from ..wavelength_support import DEFAULT_WAVELENGTH_UNITS

# from contextlib import nullcontext as does_not_raise



NORMAL_HINTED = Kind.hinted | Kind.normal


class Fourc(DiffractometerBase):
    """Test case."""

    h = Cpt(PseudoSingle, "", kind=NORMAL_HINTED)  # noqa: E741
    k = Cpt(PseudoSingle, "", kind=NORMAL_HINTED)  # noqa: E741
    l = Cpt(PseudoSingle, "", kind=NORMAL_HINTED)  # noqa: E741

    omega = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=NORMAL_HINTED)
    chi = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=NORMAL_HINTED)
    phi = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=NORMAL_HINTED)
    tth = Cpt(SoftPositioner, limits=(-170, 170), init_pos=0, kind=NORMAL_HINTED)

    h2 = Cpt(PseudoSingle, "", kind=NORMAL_HINTED)  # noqa: E741
    k2 = Cpt(PseudoSingle, "", kind=NORMAL_HINTED)  # noqa: E741
    l2 = Cpt(PseudoSingle, "", kind=NORMAL_HINTED)  # noqa: E741

    psi = Cpt(SoftPositioner, limits=(-170, 170), init_pos=0, kind=NORMAL_HINTED)


class Th2Th(DiffractometerBase):
    """Test case."""

    q = Cpt(PseudoSingle, "", kind=NORMAL_HINTED)  # noqa: E741

    th = Cpt(SoftPositioner, limits=(-90, 90), init_pos=0, kind=NORMAL_HINTED)
    tth = Cpt(SoftPositioner, limits=(-170, 170), init_pos=0, kind=NORMAL_HINTED)


class TwoC(DiffractometerBase):
    """Test case with custom names and additional axes."""

    # sorted alphabetically
    d_spacing = Cpt(PseudoSingle, "", kind=NORMAL_HINTED)  # noqa: E741
    q = Cpt(PseudoSingle, "", kind=NORMAL_HINTED)  # noqa: E741
    theta = Cpt(SoftPositioner, limits=(-90, 90), init_pos=0, kind=NORMAL_HINTED)
    ttheta = Cpt(SoftPositioner, limits=(-170, 170), init_pos=0, kind=NORMAL_HINTED)
    x = Cpt(SoftPositioner, limits=(-10, 855), init_pos=0, kind=NORMAL_HINTED)


def test_DiffractometerBase():
    with pytest.raises((DiffractometerError, ValueError)) as reason:
        DiffractometerBase("", name="dbase")
    if reason.type == "ValueError":
        assert "Must have at least 1 positioner" in str(reason)
    if reason.type == "DiffractometerError":
        assert "Pick one of these" in str(reason), f"{reason.value=!r}"


@pytest.mark.parametrize(
    "geometry, npseudos, nreals", [[Fourc, 6, 5], [Th2Th, 1, 2], [TwoC, 2, 3]]
)
@pytest.mark.parametrize(
    "solver, gname",
    [["no_op", ""], ["hkl_soleil", "E4CV"], ["th_tth", "TH TTH Q"]],
)
def test_goniometer(solver, gname, geometry, npseudos, nreals):
    goniometer = geometry("", name="goniometer")
    assert goniometer is not None
    assert len(goniometer.pseudo_positioners) == npseudos
    assert len(goniometer._pseudo) == npseudos
    assert len(goniometer.real_positioners) == nreals
    assert len(goniometer._real) == nreals
    assert not goniometer.moving

    # test the wavelength
    assert math.isclose(goniometer.wavelength.get(), DEFAULT_WAVELENGTH, abs_tol=0.001)
    assert goniometer.wavelength_units.get() == DEFAULT_WAVELENGTH_UNITS

    # # test the solver
    # assert hasattr(goniometer, "solver_name")
    # assert goniometer.solver_name == "", f"{goniometer.solver_name=!r}"
    # assert hasattr(goniometer, "solver")
    # with does_not_raise() as reason:
    #     value = goniometer.solver.get()
    # assert reason is None
    # assert isinstance(value, str), f"{value=!r} {reason=!r}"
    # assert value == "", f"{value=!r} {solver=!r} {reason=!r}"

    # with does_not_raise() as reason:
    #     goniometer.position
    # assert reason is None
    # with does_not_raise() as reason:
    #     goniometer.report
    # assert reason is None

    # solver_object = solver_factory(solver, geometry=gname)
    # assert solver_object is not None
    # assert solver_object.name == solver


def test_extras():
    # solver_name = "hkl_soleil"
    fourc = Fourc("", name="fourc")
    assert fourc is not None
    # , solver=solver_name, geometry="E4CV"
    # assert "solver_name" in dir(fourc), f"{dir(fourc)!r}"
    # assert fourc.solver_name == solver_name, f"{fourc!r}"
    # assert fourc.solver.get() == solver_name

    # solver_klass = get_solver(solver_name)
    # solver = solver_klass(
    #     geometry="E4CV",
    #     pseudos=[fourc.h, fourc.k, fourc.l],  # TODO: add to constructor
    #     reals=[fourc.omega, fourc.chi, fourc.phi, fourc.tth],
    #     extras=[fourc.h2, fourc.k2, fourc.l2, fourc.psi],
    # )
    # assert solver is not None
    # TODO:
