"""Test the hklpy2.ops module."""

import uuid
from collections import namedtuple
from contextlib import nullcontext as does_not_raise

import pytest

from ..diffract import DiffractometerBase
from ..geom import creator
from ..ops import Operations
from ..ops import OperationsError
from ..user import set_diffractometer
from ..user import setor
from .common import assert_context_result
from .models import AugmentedFourc
from .models import MultiAxis99
from .models import TwoC

SKIP_EXACT_VALUE_TEST = str(uuid.uuid4())

fourc = creator(name="fourc")


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
    assert isinstance(diffractometer.core, Operations), f"{geometry=} {solver=} {name=}"

    db = diffractometer.core._asdict()
    assert db["name"] == name

    # Walk through the keypath, revising the db object at each step
    for k in keypath.split("."):
        db = db.get(k)  # narrow the search
        assert db is not None, f"{k=!r}"  # Ensure the path exists, so far.

    if value == SKIP_EXACT_VALUE_TEST:
        assert value is not None  # Anything BUT 'None'
    else:
        assert value == db, f"{value=!r}  {db=!r}"


def test_axes_xref_empty():
    expected = "Did you forget to call `assign_axes()`"
    with pytest.raises(OperationsError) as reason:
        e4cv = creator(name="e4cv", auto_assign=False)
        e4cv.add_reflection((1, 0, 0), (10, 0, 0, 20), name="r1")
    assert_context_result(expected, reason)


@pytest.mark.filterwarnings("error")
@pytest.mark.parametrize(
    "pseudos, context, expected",
    [
        # * dict: {"h": 0, "k": 1, "l": -1}
        # * namedtuple: (h=0.0, k=1.0, l=-1.0)
        # * ordered list: [0, 1, -1]  (for h, k, l)
        # * ordered tuple: (0, 1, -1)  (for h, k, l)
        [dict(h=1, k=2, l=3), does_not_raise(), None],
        [[1, 2, 3], does_not_raise(), None],
        [(1, 2, 3), does_not_raise(), None],
        [
            namedtuple("PseudoTuple", "h k l".split())(1, 2, 3),
            does_not_raise(),
            None,
        ],
        [
            [1, 2, 3, 4],
            pytest.raises(UserWarning),
            "Extra inputs will be ignored. Expected 3.",
        ],
        [
            dict(h=1, k=2, lll=3),
            pytest.raises(KeyError),
            "Missing axis 'l'",
        ],
        [
            "abc",
            pytest.raises(TypeError),
            "Expected 'AnyAxesType'.",
        ],
    ],
)
def test_standardize_pseudos(pseudos, context, expected):
    with context as reason:
        fourc.core.standardize_pseudos(pseudos)
    assert_context_result(expected, reason)


@pytest.mark.filterwarnings("error")
@pytest.mark.parametrize(
    "reals, context, expected",
    [
        [
            dict(omega=1, chi=2, phi=3, tth=4),
            does_not_raise(),
            None,
        ],
        [[1, 2, 3, 4], does_not_raise(), None],
        [(1, 2, 3, 4), does_not_raise(), None],
        [None, does_not_raise(), None],
        [
            [1, 2, 3, 4, 5],
            pytest.raises(UserWarning),
            "Extra inputs will be ignored. Expected 4.",
        ],
        [
            dict(theta=1, chi=2, phi=3, ttheta=4),
            pytest.raises(KeyError),
            "Missing axis 'omega'.",
        ],
        [
            "abcd",
            pytest.raises(TypeError),
            "Expected 'AnyAxesType'.",
        ],
    ],
)
def test_standardize_reals(reals, context, expected):
    with context as reason:
        fourc.core.standardize_reals(reals)
    assert_context_result(expected, reason)


def test_unknown_reflection():
    sim = creator(name="sim")
    set_diffractometer(sim)
    r1 = setor(1, 0, 0, 10, 0, 0, 20)

    with pytest.raises(KeyError) as reason:
        sim.core.calc_UB(r1, "r_unknown")
    assert_context_result(" unknown.  Knowns: ", reason)


def test_assign_axes_error():
    flaky = creator(
        name="flaky",
        pseudos="h k l".split(),
        reals=dict(a=1, b=2, c=3, d=4),
    )
    assert flaky.pseudo_axis_names == "h k l".split()
    assert flaky.real_axis_names == "a b c d".split()
    with pytest.raises(ValueError) as reason:
        flaky.core.assign_axes("h k l".split(), "h b c d".split())
    expected = "Axis name cannot be in more than list."
    assert_context_result(expected, reason)


def test_repeat_sample():
    geom = creator(name="geom")
    with pytest.raises(OperationsError) as reason:
        geom.add_sample("sample", 4.1)
    expected = "Sample name='sample' already defined."
    assert_context_result(expected, reason)


@pytest.mark.parametrize(
    "gonio, axes, prop, context, expected",
    [
        [fourc, "h k l".split(), "local_pseudo_axes", does_not_raise(), None],
        [
            creator(name="k4cv", geometry="K4CV"),
            "h k l".split(),
            "local_pseudo_axes",
            does_not_raise(),
            None,
        ],
        [
            creator(name="sixc", geometry="E6C", solver_kwargs=dict(engine="psi")),
            ["psi"],
            "local_pseudo_axes",
            does_not_raise(),
            None,
        ],
        [
            AugmentedFourc(name="acccc"),
            "h k l".split(),
            "local_pseudo_axes",
            does_not_raise(),
            None,
        ],
        [
            TwoC(name="cc"),
            ["another"],
            "local_pseudo_axes",
            pytest.raises(AssertionError),
            "assert ['q'] == ['another']",
        ],
        [TwoC(name="cc"), ["q"], "local_pseudo_axes", does_not_raise(), None],
        [MultiAxis99(name="ma99"), [], "local_pseudo_axes", does_not_raise(), None],
        # ------------------
        [fourc, "omega chi phi tth".split(), "local_real_axes", does_not_raise(), None],
        [
            creator(name="k4cv", geometry="K4CV"),
            "komega kappa kphi tth".split(),
            "local_real_axes",
            does_not_raise(),
            None,
        ],
        [
            creator(name="sixc", geometry="E6C", solver_kwargs=dict(engine="psi")),
            "mu omega chi phi gamma delta".split(),
            "local_real_axes",
            does_not_raise(),
            None,
        ],
        [
            AugmentedFourc(name="acccc"),
            "omega chi phi tth".split(),
            "local_real_axes",
            does_not_raise(),
            None,
        ],
        [
            TwoC(name="cc"),
            ["another"],
            "local_real_axes",
            pytest.raises(AssertionError),
            "assert ['theta', 'ttheta'] == ['another']",
        ],
        [
            TwoC(name="cc"),
            ["theta", "ttheta"],
            "local_real_axes",
            does_not_raise(),
            None,
        ],
        [MultiAxis99(name="ma99"), [], "local_real_axes", does_not_raise(), None],
    ],
)
def test_local_pseudo_axes(gonio, axes, prop, context, expected):
    with context as reason:
        assert getattr(gonio.core, prop) == axes
    assert_context_result(expected, reason)


# FIXME: reset_samples is not tested yet
# FIXME: remove_sample is not tested yet
