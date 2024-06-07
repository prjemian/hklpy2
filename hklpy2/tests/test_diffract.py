"""Test the hklpy2.diffract module."""

import math
from contextlib import nullcontext as does_not_raise

import pytest

from ..diffract import DiffractometerBase
from ..diffract import DiffractometerError
from ..diffract import pick_first_item
from ..operations.reflection import ReflectionError
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


def test_orientation():
    from ..geom import SimulatedE4CV
    from ..operations.lattice import SI_LATTICE_PARAMETER

    fourc = SimulatedE4CV("", name="fourc")
    fourc.add_sample("silicon", SI_LATTICE_PARAMETER)
    fourc.wavelength.put(1.0)
    assert math.isclose(
        fourc.wavelength.get(), 1.0, abs_tol=0.01
    ), f"{fourc.wavelength.get()=!r}"

    fourc.add_reflection(
        (4, 0, 0),
        dict(tth=69.0966, omega=-145.451, chi=0, phi=0),
        wavelength=1.54,
        name="(400)",
    )
    fourc.add_reflection(
        (0, 4, 0),
        dict(tth=69.0966, omega=-145.451, chi=90, phi=0),
        wavelength=1.54,
        name="(040)",
    )

    assert math.isclose(
        fourc.wavelength.get(), 1.0, abs_tol=0.01
    ), f"{fourc.wavelength.get()=!r}"
    assert fourc.operator.sample.reflections.order == "(400) (040)".split()

    result = fourc.operator.calcUB(*fourc.operator.sample.reflections.order)
    assert result is None

    UB = fourc.operator.solver.UB
    assert len(UB) == 3

    UBe = [[0, 0, -1.157], [0, -1.157, 0], [-1.157, 0, 0]]
    for row, row_expected in zip(UB, UBe):
        assert len(row) == len(row_expected)
        assert isinstance(row[0], (float, int)), f"{row=!r}"

    for i in range(3):
        for j in range(3):
            assert math.isclose(
                UB[i][j], UBe[i][j], abs_tol=0.005
            ), f"{i=!r}  {j=!r}  {UB=!r}  {UBe=!r}  {UB=!r}"

    result = fourc.forward(4, 0, 0)
    assert math.isclose(result.omega, -158.39, abs_tol=0.02), f"{result=!r}"
    assert math.isclose(result.chi, 0, abs_tol=0.02), f"{result=!r}"
    assert math.isclose(result.phi, 0, abs_tol=0.02), f"{result=!r}"
    assert math.isclose(result.tth, 43.22, abs_tol=0.02), f"{result=!r}"

    result = fourc.forward(4, 0, 0, wavelength=1.54)
    assert math.isclose(result.omega, -145.45, abs_tol=0.02), f"{result=!r}"
    assert math.isclose(result.chi, 0, abs_tol=0.02), f"{result=!r}"
    assert math.isclose(result.phi, 0, abs_tol=0.02), f"{result=!r}"
    assert math.isclose(result.tth, 69.098, abs_tol=0.02), f"{result=!r}"

    assert math.isclose(  # still did not change the diffractometer wavelength
        fourc.wavelength.get(), 1.0, abs_tol=0.01
    ), f"{fourc.wavelength.get()=!r}"

    result = fourc.inverse(-145, 0, 0, 70)
    assert math.isclose(result.h, 6.23, abs_tol=0.02), f"{result=!r}"
    assert math.isclose(result.k, 0, abs_tol=0.02), f"{result=!r}"
    assert math.isclose(result.l, 0, abs_tol=0.02), f"{result=!r}"

    result = fourc.inverse(-145, 0, 0, 70, wavelength=1.54)
    assert math.isclose(result.h, 4.05, abs_tol=0.02), f"{result=!r}"
    assert math.isclose(result.k, 0, abs_tol=0.02), f"{result=!r}"
    assert math.isclose(result.l, 0, abs_tol=0.02), f"{result=!r}"


def test_set_UB():
    from ..geom import SimulatedE4CV

    UBe = [[0, 0, -1.157], [0, -1.157, 0], [-1.157, 0, 0]]
    fourc = SimulatedE4CV("", name="fourc")

    fourc.operator.solver.UB = UBe
    UBr = fourc.operator.solver.UB
    assert len(UBr) == len(UBe)

    result = fourc.inverse(-145, 0, 0, 70, wavelength=1.54)
    assert math.isclose(result.h, 4.05, abs_tol=0.02), f"{result=!r}"
    assert math.isclose(result.k, 0, abs_tol=0.02), f"{result=!r}"
    assert math.isclose(result.l, 0, abs_tol=0.02), f"{result=!r}"


@pytest.mark.parametrize(
    "name, pseudos, reals, wavelength, replace, num, raiser, excuse",
    [
        ["(100)", (1, 0, 0), (10, 0, 0, 20), 1, True, 1, does_not_raise(), None],
        [
            "(100)",
            (1, 0, 0),
            (10, 0, 0, 20),
            1,
            False,
            1,
            pytest.raises(ReflectionError),
            "Use 'replace=True' to overwrite.",
        ],
        ["r2", (1, 0, 0), (10, 0, 0, 20), 1, True, 1, does_not_raise(), None],
        ["r2", (2, 0, 0), (10, 0, 0, 20), 1, False, 2, does_not_raise(), None],
        ["r2", (1, 0, 0), (10, 10, 0, 20), 1, False, 2, does_not_raise(), None],
        ["(100)", (1, 0, 0), (10, 10, 0, 20), 1, True, 1, does_not_raise(), None],
        [
            "r2",  # different name
            (1, 0, 0),  # same data
            (10, 0, 0, 20),  # same data
            1,  # same data
            False,
            1,
            pytest.raises(ReflectionError),
            "Use 'replace=True' to overwrite.",
        ],
        [
            "r2",  # different name
            (1, 0, 0),  # same data
            (10, 0, 0, 20),  # same data
            1.5,  # different data
            False,
            2,
            does_not_raise(),
            None,
        ],
    ],
)
def test_repeated_reflections(
    name, pseudos, reals, wavelength, replace, num, raiser, excuse
):
    from ..geom import SimulatedE4CV

    e4cv = SimulatedE4CV("", name="e4cv")
    e4cv.add_reflection(
        dict(h=1, k=0, l=0),
        dict(omega=10, chi=0, phi=0, tth=20),
        wavelength=1.0,
        name="(100)",
    )
    assert len(e4cv.sample.reflections) == 1

    with raiser as reason:
        e4cv.add_reflection(
            pseudos,
            reals,
            name=name,
            wavelength=wavelength,
            replace=replace,
        )
    if excuse is not None:
        assert excuse in str(reason), f"{reason=!r}  {excuse=!r}"
    assert len(e4cv.sample.reflections) == num, f"{e4cv.sample.reflections=!r}"
