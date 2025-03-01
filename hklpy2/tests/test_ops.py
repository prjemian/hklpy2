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
    assert isinstance(
        diffractometer.operator, Operations
    ), f"{geometry=} {solver=} {name=}"

    db = diffractometer.operator._asdict()
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


@pytest.mark.parametrize(
    "pseudos, names, context, expected",
    [
        # * dict: {"h": 0, "k": 1, "l": -1}
        # * namedtuple: (h=0.0, k=1.0, l=-1.0)
        # * ordered list: [0, 1, -1]  (for h, k, l)
        # * ordered tuple: (0, 1, -1)  (for h, k, l)
        [dict(h=1, k=2, l=3), fourc.pseudo_axis_names, does_not_raise(), None],
        [[1, 2, 3], fourc.pseudo_axis_names, does_not_raise(), None],
        [(1, 2, 3), fourc.pseudo_axis_names, does_not_raise(), None],
        [
            namedtuple("HklPos", "h k l".split())(1, 2, 3),
            fourc.pseudo_axis_names,
            does_not_raise(),
            None,
        ],
        [
            [1, 2, 3, 4],
            fourc.pseudo_axis_names,
            pytest.raises(ValueError),
            "pseudos, received",
        ],
        [
            dict(h=1, k=2, lll=3),
            fourc.pseudo_axis_names,
            pytest.raises(OperationsError),
            "Missing axis",
        ],
        [
            "abc",
            fourc.pseudo_axis_names,
            pytest.raises(OperationsError),
            "Unexpected type",
        ],
    ],
)
def test_standardize_pseudos(pseudos, names, context, expected):
    with context as reason:
        fourc.operator.standardize_pseudos(pseudos, names)
    assert_context_result(expected, reason)


@pytest.mark.parametrize(
    "reals, names, context, expected",
    [
        [
            dict(omega=1, chi=2, phi=3, tth=4),
            fourc.real_axis_names,
            does_not_raise(),
            None,
        ],
        [[1, 2, 3, 4], fourc.real_axis_names, does_not_raise(), None],
        [(1, 2, 3, 4), fourc.real_axis_names, does_not_raise(), None],
        [None, fourc.real_axis_names, does_not_raise(), None],
        [
            namedtuple("RealPos", "a b c d".split())(1, 2, 3, 4),
            "a b c d".split(),
            does_not_raise(),
            None,
        ],
        [
            [1, 2, 3, 4, 5],
            fourc.real_axis_names,
            pytest.raises(ValueError),
            "reals, received",
        ],
        [
            dict(theta=1, chi=2, phi=3, ttheta=4),
            fourc.real_axis_names,
            pytest.raises(OperationsError),
            "Missing axis",
        ],
        [
            "abcd",
            fourc.real_axis_names,
            pytest.raises(OperationsError),
            "Unexpected type",
        ],
    ],
)
def test_standardize_reals(reals, names, context, expected):
    with context as reason:
        fourc.operator.standardize_reals(reals, names)
    assert_context_result(expected, reason)


def test_unknown_reflection():
    sim = creator(name="sim")
    set_diffractometer(sim)
    r1 = setor(1, 0, 0, 10, 0, 0, 20)

    with pytest.raises(KeyError) as reason:
        sim.operator.calc_UB(r1, "r_unknown")
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
        flaky.operator.assign_axes("h k l".split(), "h b c d".split())
    expected = "Axis name cannot be in more than list."
    assert_context_result(expected, reason)


def test_repeat_sample():
    geom = creator(name="geom")
    with pytest.raises(OperationsError) as reason:
        geom.add_sample("sample", 4.1)
    expected = "Sample name='sample' already defined."
    assert_context_result(expected, reason)


# FIXME: reset_samples is not tested yet
# FIXME: remove_sample is not tested yet
