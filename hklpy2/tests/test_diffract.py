"""Test the hklpy2.diffract module."""

import math
from collections import deque
from collections import namedtuple
from contextlib import nullcontext as does_not_raise

import bluesky
import pytest
from gi.repository.GLib import GError
from numpy.testing import assert_almost_equal
from ophyd.sim import noisy_det

from ..diffract import DiffractometerBase
from ..diffract import pick_first_item
from ..geom import creator
from ..operations.misc import DiffractometerError
from ..operations.reflection import ReflectionError
from ..operations.sample import Sample
from ..ops import DEFAULT_SAMPLE_NAME
from ..ops import Operations
from ..ops import OperationsError
from ..wavelength_support import DEFAULT_WAVELENGTH
from ..wavelength_support import DEFAULT_WAVELENGTH_UNITS
from .common import HKLPY2_DIR
from .common import assert_context_result
from .models import AugmentedFourc
from .models import Fourc
from .models import MultiAxis99
from .models import NoOpTh2Th
from .models import TwoC


def test_choice_function():
    choice = pick_first_item((), "a b c".split())
    assert choice == "a"


def test_DiffractometerBase():
    with pytest.raises((DiffractometerError, ValueError)) as reason:
        DiffractometerBase(name="dbase")
    if reason.type == "ValueError":
        assert "Must have at least 1 positioner" in str(reason)


@pytest.mark.parametrize("axis", "h k l".split())
@pytest.mark.parametrize(
    "value, context, expected",
    [
        [-1, does_not_raise(), None],
        [1, does_not_raise(), None],
        [-1.2, does_not_raise(), None],
        [1.2, does_not_raise(), None],
        [12, pytest.raises(GError), "unreachable hkl"],
        [-12, pytest.raises(GError), "unreachable hkl"],
    ],
)
def test_limits(axis, value, context, expected):
    with context as reason:
        fourc = creator(name="fourc")
        assert hasattr(fourc, axis)
        pseudo = getattr(fourc, axis)
        assert pseudo.limits == (0, 0)
        assert pseudo.check_value(value) is None

    assert_context_result(expected, reason)


@pytest.mark.parametrize(
    "dclass, np, nr, solver, gname, solver_kwargs, pseudos, reals",
    [
        [Fourc, 3, 4, None, None, {}, [], []],
        [AugmentedFourc, 7, 8, None, None, {}, [], []],
        [MultiAxis99, 9, 9, "hkl_soleil", "E4CV", {}, [], []],
        [
            MultiAxis99,
            9,
            9,
            "hkl_soleil",
            "E4CV",
            {},
            "p1 p2 p3 p4".split(),
            "r1 r2 r3 r4".split(),
        ],
        [MultiAxis99, 9, 9, "no_op", "test", {}, [], []],
        [MultiAxis99, 9, 9, "th_tth", "TH TTH Q", {}, [], []],
        [NoOpTh2Th, 1, 2, None, None, {}, [], []],
        [TwoC, 2, 4, None, None, {}, [], []],
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
):
    """Test each diffractometer class."""
    dmeter = dclass("", name="goniometer")
    assert dmeter is not None
    if solver is not None:
        dmeter.operator.set_solver(solver, gname, **solver_kwargs)

    if len(pseudos) == 0:
        if solver is not None:
            dmeter.auto_assign_axes()
    else:
        dmeter.operator.assign_axes(pseudos, reals)

    with does_not_raise():
        # These PseudoPositioner properties _must_ work immediately.
        assert isinstance(dmeter.position, tuple), f"{type(dmeter.position)=!r}"
        assert isinstance(dmeter.report, dict), f"{type(dmeter.report)=!r}"

    if solver is not None:
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
            dmeter._source.wavelength,
            dmeter.wavelength.get(),
            abs_tol=0.001,
        )
        assert math.isclose(
            dmeter._source.wavelength,
            DEFAULT_WAVELENGTH,
            abs_tol=0.001,
        )
        assert dmeter._source.wavelength_units == DEFAULT_WAVELENGTH_UNITS

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


def test_diffractometer_wh(capsys):
    from ..geom import creator

    e4cv = creator(name="e4cv")
    e4cv.restore(HKLPY2_DIR / "tests" / "e4cv_orient.yml")

    e4cv.wh()
    captured = capsys.readouterr()
    lines = captured.out.splitlines()
    assert len(lines) == 3, f"{captured.out=}"
    assert lines[1].startswith("wavelength=")
    assert lines[0].startswith("h=")
    assert lines[2].startswith("omega=")

    e4cv.operator.solver.mode = "psi_constant"
    e4cv.wh(full=True)
    captured = capsys.readouterr()
    lines = captured.out.splitlines()
    expected = """
        diffractometer=
        HklSolver(name
        Sample(name=
    """.strip().split()
    for _r in e4cv.operator.sample.reflections:
        expected.append("Reflection(name='")
    expected.append("Orienting reflections: ")
    expected.append("U=")
    expected.append("UB=")
    for _r in e4cv.operator.constraints:
        expected.append("constraint: ")
    expected.append(f"{e4cv.pseudo_axis_names[0]}=")
    expected.append("wavelength=")
    expected.append(f"{e4cv.real_axis_names[0]}=")
    extra_names = e4cv.operator.solver.extra_axis_names
    if len(extra_names) > 0:
        expected.append(f"{extra_names[0]}=")
    assert len(lines) == len(expected), f"{captured.out=}"
    for actual, exp in zip(lines, expected):
        assert actual.startswith(exp)


@pytest.mark.parametrize(
    "mode, keys, context, expected, config_file",
    [
        [
            "bissector",
            "h k l omega chi phi tth".split(),
            does_not_raise(),
            None,
            "e4cv_orient.yml",
        ],
        [
            "bissector",
            "h k l omega chi phi tth".split(),
            does_not_raise(),
            None,
            "fourc-configuration.yml",
        ],
    ],
)
def test_full_position(mode, keys, context, expected, config_file):
    from ..geom import creator

    assert config_file.endswith(".yml")

    with context as reason:
        fourc = creator(name="fourc")
        fourc.restore(HKLPY2_DIR / "tests" / config_file)
        fourc.operator.solver.mode = mode
        pos = fourc.full_position()
        assert isinstance(pos, dict)

    assert_context_result(expected, reason)


@pytest.mark.parametrize(
    "pseudos, reals, mode, context, expected",
    [
        [
            dict(h=1, k=1, l=0),
            dict(h2=1, k2=1, l2=1, psi=0),
            "psi_constant",
            does_not_raise(),
            None,
        ],
    ],
)
def test_move_forward_with_extras(pseudos, reals, mode, context, expected):
    from ..geom import creator

    fourc = creator(name="fourc")
    fourc.restore(HKLPY2_DIR / "tests" / "e4cv_orient.yml")
    fourc.operator.solver.mode = mode
    # fourc.wavelength.put(6)
    assert fourc.operator.solver.mode == mode

    RE = bluesky.RunEngine()

    with context as reason:
        RE(fourc.move_forward_with_extras(pseudos, reals))

    assert_context_result(expected, reason)


@pytest.mark.parametrize(
    "pos, context, expected",
    [
        [(1, 2, 3, 4), does_not_raise(), None],
        [{"omega": 1, "chi": 2, "phi": 3, "tth": 4}, does_not_raise(), None],
        [
            namedtuple(
                "RealPosition", "omega chi phi tth".split(), defaults=[1, 2, 3, 4]
            )(),
            does_not_raise(),
            None,
        ],
        [(1, 2, 3, 4, 5, 6), pytest.raises(ValueError), "too many args"],
        [
            {"omega": 1, "chi": 2, "phi": 3, "delta": -4},
            pytest.raises(TypeError),
            "unexpected keyword argument 'delta'",
        ],
    ],
)
def test_move_reals(pos, context, expected):
    from ..geom import creator

    fourc = creator(name="fourc")
    with context as reason:
        fourc.move_reals(pos)

    assert_context_result(expected, reason)


def test_null_operator():
    """Tests special cases when diffractometer.operator is None."""
    from ..geom import creator

    fourc = creator(name="fourc")
    assert fourc.operator is not None
    assert len(fourc.samples) > 0
    assert fourc.sample is not None
    assert fourc.operator.solver is not None
    assert fourc.solver_name is not None

    fourc.operator._solver = None
    assert len(fourc.samples) > 0
    assert fourc.sample is not None
    assert fourc.solver_name == ""

    fourc.operator = None
    assert len(fourc.samples) == 0
    assert fourc.sample is None
    assert fourc.solver_name == ""


def test_orientation():
    from ..geom import creator
    from ..operations.lattice import SI_LATTICE_PARAMETER

    fourc = creator(name="fourc")
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

    result = fourc.operator.calc_UB(*fourc.operator.sample.reflections.order)
    assert isinstance(result, list)
    assert isinstance(result[0], list)
    assert isinstance(result[0][0], (float, int))

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
            ), f"{i=!r}  {j=!r}  {UB=!r}  {UBe=!r}"

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


def test_remove_sample():
    sim = NoOpTh2Th(name="sim")
    assert len(sim.samples) == 1
    try:
        sim.operator.remove_sample(DEFAULT_SAMPLE_NAME)
    except OperationsError as reason:
        assert_context_result("Cannot remove last sample.", reason)
    assert len(sim.samples) == 1


@pytest.mark.parametrize(
    "name, pseudos, reals, wavelength, replace, num, context, expected",
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
    name, pseudos, reals, wavelength, replace, num, context, expected
):
    from ..geom import creator

    e4cv = creator(name="e4cv")
    e4cv.add_reflection(
        dict(h=1, k=0, l=0),
        dict(omega=10, chi=0, phi=0, tth=20),
        wavelength=1.0,
        name="(100)",
    )
    assert len(e4cv.sample.reflections) == 1

    with context as reason:
        e4cv.add_reflection(
            pseudos,
            reals,
            name=name,
            wavelength=wavelength,
            replace=replace,
        )
    assert_context_result(expected, reason)
    assert len(e4cv.sample.reflections) == num, f"{e4cv.sample.reflections=!r}"


@pytest.mark.parametrize(
    "scan_kwargs, mode, context, expected",
    [
        [
            dict(
                detectors=[noisy_det],
                axis="psi",
                start=5,
                finish=10,
                num=3,
                pseudos=dict(h=1, k=1, l=0),
                reals=None,
                extras=dict(h2=1, k2=1, l2=1, psi=0),
                fail_on_exception=True,
            ),
            "psi_constant",
            does_not_raise(),
            None,
        ],
        [
            dict(
                detectors=[noisy_det],
                axis="psi",
                start=5,
                finish=10,
                num=3,
                pseudos=dict(h=2, k=-1, l=10),  # l=10 is unreachable
                reals=None,
                extras=dict(h2=2, k2=2, l2=0, psi=0),
                fail_on_exception=True,
            ),
            "psi_constant",
            pytest.raises(GError),  # TODO: #39
            "unreachable hkl",  # hkl-engine-error-quark:
        ],
        [
            dict(
                detectors=[noisy_det],
                axis="psi",
                start=5,
                finish=10,
                num=3,
                pseudos=dict(h=2, k=-1, l=0),
                reals=None,
                extras=dict(h2=2, k2=2, l2=0, psi=0),
                fail_on_exception=False,  # ignore error that failed previous test
            ),
            "psi_constant",
            does_not_raise(),
            None,
        ],
        [
            dict(
                detectors=[noisy_det],
                axis="psi",
                start=5,
                finish=10,
                num=3,
                pseudos=None,
                reals=dict(omega=1, chi=2, phi=3, tth=4),
                extras=dict(h2=2, k2=2, l2=0, psi=5),
                fail_on_exception=True,
            ),
            "psi_constant",
            pytest.raises(NotImplementedError),
            "Inverse transformation.",
        ],
        [
            dict(
                detectors=noisy_det,
            ),
            "psi_constant",
            pytest.raises(TypeError),
            " is not iterable.",
        ],
        [
            dict(
                detectors=[noisy_det],
                axis="oddball",
            ),
            "psi_constant",
            pytest.raises(KeyError),
            "'oddball' not in ",
        ],
        [
            dict(
                detectors=[noisy_det],
                axis="psi",
                pseudos=None,
                reals=None,
            ),
            "psi_constant",
            pytest.raises(ValueError),
            "Must define either pseudos or reals.",
        ],
        [
            dict(
                detectors=[noisy_det],
                axis="psi",
                pseudos=dict(h=2, k=-1, l=0),
                reals=dict(omega=1, chi=2, phi=3, tth=4),
            ),
            "psi_constant",
            pytest.raises(ValueError),
            "Cannot define both pseudos and reals.",
        ],
    ],
)
def test_scan_extra(scan_kwargs, mode, context, expected):
    from ..geom import creator

    fourc = creator(name="fourc")
    fourc.restore(HKLPY2_DIR / "tests" / "e4cv_orient.yml")
    fourc.operator.solver.mode = mode
    assert fourc.operator.solver.mode == mode

    RE = bluesky.RunEngine()

    if isinstance(scan_kwargs["detectors"], dict):
        # Avoid the test case where detectors is not iterable
        scan_kwargs["detectors"].append(fourc)

    with context as reason:
        RE(fourc.scan_extra(**scan_kwargs))

    assert_context_result(expected, reason)


def test_set_UB():
    from ..geom import creator

    UBe = [[0, 0, -1.157], [0, -1.157, 0], [-1.157, 0, 0]]
    fourc = creator(name="fourc")

    fourc.operator.solver.UB = UBe
    UBr = fourc.operator.solver.UB
    assert len(UBr) == len(UBe)

    result = fourc.inverse(-145, 0, 0, 70, wavelength=1.54)
    assert math.isclose(result.h, 4.05, abs_tol=0.02), f"{result=!r}"
    assert math.isclose(result.k, 0, abs_tol=0.02), f"{result=!r}"
    assert math.isclose(result.l, 0, abs_tol=0.02), f"{result=!r}"


def test_e4cv_constant_phi():
    from ..geom import creator

    e4cv = creator(name="e4cv")

    # Approximate the code presented as the example problem.
    refl = dict(h=1, k=1, l=1)

    e4cv.operator.solver.mode = "constant_phi"
    CONSTANT_PHI = 23.4567
    e4cv.phi.move(CONSTANT_PHI)

    e4cv.operator.constraints["phi"].limits = -180, 180

    # Check that phi is held constant in all forward solutions.
    solutions = e4cv.operator.solver.forward(refl)
    assert isinstance(solutions, list)
    assert len(solutions) > 0
    for solution in solutions:
        assert isinstance(solution, dict)
        assert_almost_equal(solution["phi"], CONSTANT_PHI, 4)

    # # Check that phi is held constant in forward()
    # # Returns a position namedtuple.
    position = e4cv.forward(refl)
    assert isinstance(position, tuple)
    assert_almost_equal(position.phi, CONSTANT_PHI, 4)


@pytest.mark.parametrize(
    "miller, context, expected",
    [
        [(1, 2, 3), does_not_raise(), None],
        [dict(h=1, k=2, l=3), does_not_raise(), None],
        [[1.0, 2.0, 3.0], does_not_raise(), None],
        [
            None,
            pytest.raises(TypeError),
            "Pseudos must be tuple, list, or dict.",
        ],
        [
            # Tests that h, k, l was omitted, only a position was supplied.
            # This is one of the problems reported.
            namedtuple("PosAnything", "a b c d".split())(1, 2, 3, 4),
            pytest.raises(ValueError),
            "Expected 3 pseudos, received ",
        ],
        [
            # Tests that wrong name(s) were supplied.
            namedtuple("PosAnything", "three wrong names".split())(1, 2, 4),
            pytest.raises(ValueError),
            "Wrong axis names",
        ],
        [("1", 2, 3), pytest.raises(TypeError), "Must be number, received "],
        [(1, 2, "3"), pytest.raises(TypeError), "Must be number, received "],
        [([1], 2, 3), pytest.raises(TypeError), "Must be number, received "],
        [(object, 2, 3), pytest.raises(TypeError), "Must be number, received "],
        [(None, 2, 3), pytest.raises(TypeError), "Must be number, received "],
        [((1,), 2, 3), pytest.raises(TypeError), "Must be number, received "],
        [deque(), pytest.raises(TypeError), "Unexpected data type"],
    ],
)
def test_miller_args(miller, context, expected):
    """Test the Miller indices arguments: h, k, l."""

    with context as reason:
        e4cv = creator(name="e4cv")
        e4cv.add_reflection(miller)
    assert_context_result(expected, reason)
