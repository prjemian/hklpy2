"""Test the hklpy2.diffract module."""

import math
from contextlib import nullcontext as does_not_raise

import pytest

from ..diffract import DiffractometerBase
from ..diffract import DiffractometerError
from ..diffract import pick_first_item
from ..operations.sample import Sample
from ..ops import Operations
from ..wavelength_support import DEFAULT_WAVELENGTH
from ..wavelength_support import DEFAULT_WAVELENGTH_UNITS
from .models import AugmentedFourc
from .models import Fourc
from .models import MultiAxis99
from .models import NoOpTh2Th
from .models import TwoC


def test_choice_function():
    choice = pick_first_item("a b c".split())
    assert choice == "a"


def test_DiffractometerBase():
    with pytest.raises((DiffractometerError, ValueError)) as reason:
        DiffractometerBase("", name="dbase")
    if reason.type == "ValueError":
        assert "Must have at least 1 positioner" in str(reason)
    if reason.type == "DiffractometerError":
        assert "Pick one of these" in str(reason), f"{reason.value=!r}"


@pytest.mark.parametrize(
    "dclass, np, nr, solver, gname, solver_kwargs, pseudos, reals, extras",
    [
        [Fourc, 3, 4, None, None, {}, [], [], []],
        [AugmentedFourc, 7, 8, None, None, {}, [], [], []],
        [MultiAxis99, 9, 9, "hkl_soleil", "E4CV", {}, [], [], []],
        [
            MultiAxis99,
            9,
            9,
            "hkl_soleil",
            "E4CV",
            {},
            "p1 p2 p3 p4".split(),
            "r1 r2 r3 r4".split(),
            [],
        ],
        [MultiAxis99, 9, 9, "no_op", "test", {}, [], [], []],
        [MultiAxis99, 9, 9, "th_tth", "TH TTH Q", {}, [], [], []],
        [NoOpTh2Th, 1, 2, None, None, {}, [], [], []],
        [TwoC, 2, 4, None, None, {}, [], [], []],
    ],
)
def test_diffractometer_class(
    dclass,
    np,
    nr,
    solver,
    gname,
    solver_kwargs,
    pseudos,
    reals,
    extras,
):
    """Test each diffractometer class."""
    dmeter = dclass("", name="goniometer")
    assert dmeter is not None
    if solver is not None:
        dmeter.operator.set_solver(solver, gname, **solver_kwargs)

    if len(pseudos) == 0:
        dmeter.auto_assign_axes()
    else:
        dmeter.operator.assign_axes(pseudos, reals, extras)

    with does_not_raise():
        # These PseudoPositioner properties _must_ work immediately.
        assert isinstance(dmeter.position, tuple), f"{type(dmeter.position)=!r}"
        assert isinstance(dmeter.report, dict), f"{type(dmeter.report)=!r}"

    # ophyd components
    assert isinstance(dmeter.geometry.get(), str)
    assert isinstance(dmeter.solver.get(), str)
    assert isinstance(dmeter.wavelength.get(), (float, int))

    assert len(dmeter.pseudo_positioners) == np
    assert len(dmeter._pseudo) == np
    assert len(dmeter.real_positioners) == nr
    assert len(dmeter._real) == nr
    assert not dmeter.moving

    # test the wavelength
    assert math.isclose(
        dmeter._wavelength.wavelength,
        dmeter.wavelength.get(),
        abs_tol=0.001,
    )
    assert math.isclose(
        dmeter._wavelength.wavelength,
        DEFAULT_WAVELENGTH,
        abs_tol=0.001,
    )
    assert dmeter._wavelength.wavelength_units == DEFAULT_WAVELENGTH_UNITS

    assert len(dmeter.samples) == 1
    assert isinstance(dmeter.sample, Sample)

    assert isinstance(dmeter.operator, Operations)
    assert isinstance(dmeter.pseudo_axis_names, list)
    assert isinstance(dmeter.real_axis_names, list)

    dmeter.operator.add_sample("test", 5)
    assert len(dmeter.samples) == 2
    assert dmeter.sample.name == "test"

    assert dmeter.solver is not None
    assert isinstance(dmeter.solver_name, str)
    assert len(dmeter.solver_name) > 0


def test_extras():
    solver_name = "hkl_soleil"
    gname = "E4CV"
    fourc = AugmentedFourc("", name="fourc")
    assert fourc is not None

    fourc.operator.set_solver(
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
