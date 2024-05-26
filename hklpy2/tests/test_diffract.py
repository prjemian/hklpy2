"""Test the hklpy2.diffract module."""

import math
from contextlib import nullcontext as does_not_raise

import pytest
from ophyd import Component as Cpt
from ophyd import Kind
from ophyd import PseudoSingle
from ophyd import SoftPositioner

from .. import SolverBase
from ..diffract import DiffractometerBase
from ..diffract import DiffractometerError
from ..operations.misc import solver_factory
from ..wavelength_support import DEFAULT_WAVELENGTH
from ..wavelength_support import DEFAULT_WAVELENGTH_UNITS

NORMAL_HINTED = Kind.hinted | Kind.normal


class Fourc(DiffractometerBase):
    """Test case."""

    h = Cpt(PseudoSingle, "", kind=NORMAL_HINTED)  # noqa: E741
    k = Cpt(PseudoSingle, "", kind=NORMAL_HINTED)  # noqa: E741
    l = Cpt(PseudoSingle, "", kind=NORMAL_HINTED)  # noqa: E741

    theta = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=NORMAL_HINTED)
    chi = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=NORMAL_HINTED)
    phi = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=NORMAL_HINTED)
    ttheta = Cpt(SoftPositioner, limits=(-170, 170), init_pos=0, kind=NORMAL_HINTED)

    # define a few more axes, extra parameters for some geometries/engines/modes

    h2 = Cpt(PseudoSingle, "", kind=NORMAL_HINTED)  # noqa: E741
    k2 = Cpt(PseudoSingle, "", kind=NORMAL_HINTED)  # noqa: E741
    l2 = Cpt(PseudoSingle, "", kind=NORMAL_HINTED)  # noqa: E741
    psi = Cpt(SoftPositioner, limits=(-170, 170), init_pos=0, kind=NORMAL_HINTED)

    # and a few more axes not used by 4-circle code

    q = Cpt(PseudoSingle, "", kind=NORMAL_HINTED)  # noqa: E741
    mu = Cpt(SoftPositioner, limits=(-170, 170), init_pos=0, kind=NORMAL_HINTED)
    nu = Cpt(SoftPositioner, limits=(-170, 170), init_pos=0, kind=NORMAL_HINTED)
    omicron = Cpt(SoftPositioner, limits=(-170, 170), init_pos=0, kind=NORMAL_HINTED)

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            solver="hkl_soleil",
            geometry="E4CV",
            solver_kwargs={"engine": "hkl"},
            **kwargs,
        )


class NoOpTh2Th(DiffractometerBase):
    """Test case."""

    q = Cpt(PseudoSingle, "", kind=NORMAL_HINTED)  # noqa: E741

    th = Cpt(SoftPositioner, limits=(-90, 90), init_pos=0, kind=NORMAL_HINTED)
    tth = Cpt(SoftPositioner, limits=(-170, 170), init_pos=0, kind=NORMAL_HINTED)

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            solver="no_op",
            geometry="TH TTH Q",
            **kwargs,
        )


class TwoC(DiffractometerBase):
    """Test case with custom names and additional axes."""

    # sorted alphabetically
    another = Cpt(PseudoSingle, "", kind=NORMAL_HINTED)  # noqa: E741
    q = Cpt(PseudoSingle, "", kind=NORMAL_HINTED)  # noqa: E741
    horizontal = Cpt(SoftPositioner, limits=(-10, 855), init_pos=0, kind=NORMAL_HINTED)
    theta = Cpt(SoftPositioner, limits=(-90, 90), init_pos=0, kind=NORMAL_HINTED)
    ttheta = Cpt(SoftPositioner, limits=(-170, 170), init_pos=0, kind=NORMAL_HINTED)
    vertical = Cpt(SoftPositioner, limits=(-10, 855), init_pos=0, kind=NORMAL_HINTED)

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            solver="th_tth",
            geometry="TH TTH Q",
            pseudos=["q"],
            reals="theta ttheta".split(),
            **kwargs,
        )


def test_DiffractometerBase():
    with pytest.raises((DiffractometerError, ValueError)) as reason:
        DiffractometerBase("", name="dbase")
    if reason.type == "ValueError":
        assert "Must have at least 1 positioner" in str(reason)
    if reason.type == "DiffractometerError":
        assert "Pick one of these" in str(reason), f"{reason.value=!r}"


@pytest.mark.parametrize(
    "dclass, npseudos, nreals", [[Fourc, 7, 8], [NoOpTh2Th, 1, 2], [TwoC, 2, 4]]
)
@pytest.mark.parametrize(
    "solver, gname",
    [["no_op", "th_tth"], ["hkl_soleil", "E4CV"], ["th_tth", "TH TTH Q"]],
)
def test_goniometer(solver, gname, dclass, npseudos, nreals):
    diffractometer = dclass("", name="goniometer")
    assert diffractometer is not None
    assert len(diffractometer.pseudo_positioners) == npseudos
    assert len(diffractometer._pseudo) == npseudos
    assert len(diffractometer.real_positioners) == nreals
    assert len(diffractometer._real) == nreals
    assert not diffractometer.moving

    # test the wavelength
    assert math.isclose(
        diffractometer._wavelength.wavelength,
        DEFAULT_WAVELENGTH,
        abs_tol=0.001,
    )
    assert diffractometer._wavelength.wavelength_units == DEFAULT_WAVELENGTH_UNITS

    # test the solver
    diffractometer.set_solver(solver, gname)
    assert hasattr(diffractometer, "solver_name")
    assert hasattr(diffractometer, "operator")
    assert hasattr(diffractometer.operator, "solver")
    assert diffractometer.operator.solver is not None
    assert isinstance(diffractometer.operator.solver, SolverBase)
    assert isinstance(diffractometer.operator.solver.name, str)
    assert diffractometer.solver_name == solver, f"{diffractometer.solver_name=!r}"
    # TODO: assertions for actual solver object

    with does_not_raise() as reason:
        diffractometer.position
    assert reason is None
    with does_not_raise() as reason:
        diffractometer.report
    assert reason is None

    solver_object = solver_factory(solver, gname)
    assert solver_object is not None
    assert solver_object.name == solver


def test_extras():
    solver_name = "hkl_soleil"
    gname = "E4CV"
    fourc = Fourc("", name="fourc")
    assert fourc is not None

    fourc.set_solver(
        solver_name,
        gname,
        pseudos=[fourc.h, fourc.k, fourc.l],
        reals=[fourc.theta, fourc.chi, fourc.phi, fourc.ttheta],
        extras=[fourc.h2, fourc.k2, fourc.l2, fourc.psi],
    )
    assert "solver_name" in dir(fourc), f"{dir(fourc)!r}"
    assert fourc.solver_name == solver_name, f"{fourc!r}"

    fourc.operator.solver.mode = "psi_constant"
    assert fourc.operator.solver.pseudo_axis_names == "h k l".split()
    assert fourc.operator.solver.real_axis_names == "omega chi phi tth".split()
    assert fourc.operator.solver.extra_axis_names == "h2 k2 l2 psi".split()

    # TODO:


def test_remove_sample():
    sim = NoOpTh2Th("", name="sim")
    assert len(sim.samples) == 1
    sim.operator.remove_sample("cubic")
    assert len(sim.samples) == 0
