from contextlib import nullcontext as does_not_raise

import pytest

from .. import SolverBase
from .. import get_solver
from ..misc import unique_name
from ..reflection import Reflection
from ..reflection import ReflectionsDict

no_op_solver = get_solver("no_op")()


def test_reflection_no_op():
    """Test with the NoOpSolver"""
    from ..backends.no_op import NoOpSolver

    solver = NoOpSolver()
    assert solver is not None

    g = solver.setGeometry("No geometry")
    assert g is None  # NoOpSolver always returns None for geometry

    ref1 = Reflection(solver, {}, {}, 1.0, name="r1")
    assert ref1 is not None
    assert ref1.name == "r1"
    expected = (
        "Reflection(name='r1', pseudos={}, angles={}, "
        "wavelength=1.0, geometry='No geometry')"
    )
    assert str(ref1) == expected, f"{ref1}"

    ref2 = Reflection(solver, {}, {}, 1.01)
    assert ref2 is not None
    assert ref2.name != "r2"
    assert len(ref2.name) == len(unique_name())


def test_reflection_hkl_soleil():
    """Test with the HklSolver"""
    from ..backends.hkl_soleil import HklSolver

    solver = HklSolver()
    assert solver is not None

    g = solver.setGeometry("E4CV", "hkl")
    assert g is not None

    reals = dict(omega=10, chi=0, phi=0, tth=20)
    pseudos = dict(h=1, k=0, l=0)
    ref1 = Reflection(solver, pseudos, reals, 1.0, name="r1")
    assert ref1.name == "r1"
    expected = (
        "Reflection(name='r1', pseudos={'h': 1, 'k': 0, 'l': 0}, "
        "angles={'omega': 10, 'chi': 0, 'phi': 0, 'tth': 20}, "
        "wavelength=1.0, geometry='E4CV')"
    )
    assert str(ref1) == expected, f"{ref1}"


def test_with_solver_base():
    """Special case that does not fit constructor test."""
    reason = "Can't instantiate abstract class SolverBase"
    with pytest.raises(TypeError) as excuse:
        Reflection(SolverBase(), None, None, None, name="solver")
    assert reason in str(excuse.value), f"{excuse=}"


@pytest.mark.parametrize(
    "solver, pseudos, angles, wavelength, rname, outcome, reason",
    [
        [
            no_op_solver,
            None,
            None,
            None,
            None,
            pytest.raises(TypeError),
            "Must supply dict, received pseudos=",
        ],
        [
            no_op_solver,
            {},
            None,
            None,
            None,
            pytest.raises(TypeError),
            "Must supply dict, received angles=",
        ],
        [
            no_op_solver,
            {},
            {},
            None,
            None,
            pytest.raises(TypeError),
            "Must supply number, received wavelength=",
        ],
        [
            no_op_solver,
            {},
            {},
            -1,
            None,
            pytest.raises(ValueError),
            "Must be >=0, received wavelength=",
        ],
        [
            no_op_solver,
            {},
            {},
            0,
            None,
            does_not_raise(),
            None,
        ],
        [
            no_op_solver,
            {},
            {},
            0,
            "reflection",
            does_not_raise(),
            None,
        ],
    ],
)
def test_reflection_constructor(
    solver, pseudos, angles, wavelength, rname, outcome, reason
):
    with outcome as excuse:
        reflection = Reflection(solver, pseudos, angles, wavelength, name=rname)
        assert reflection is not None
        if rname is None:
            assert isinstance(reflection.name, str)
            assert len(reflection.name) == len(unique_name())
        else:
            assert reflection.name == rname
        assert reflection.pseudos == pseudos
        assert reflection.angles == angles
        assert reflection.wavelength == wavelength

    if reason is not None:
        assert reason in str(excuse.value), f"{excuse=}"


@pytest.mark.parametrize(
    "outcome, reason",
    [[does_not_raise(), None]],
)
def test_reflectionsdict_constructor(outcome, reason):
    with outcome as excuse:
        rdict = ReflectionsDict()
        assert rdict is not None
        assert rdict.ordering == []
        assert rdict.set_or == rdict.set_orientation_reflections

    if reason is not None:
        assert reason in str(excuse.value), f"{excuse=}"


def test_reflectionsdict_swap():
    rdict = ReflectionsDict()
    assert rdict is not None
    assert rdict.ordering == []

    rdict.ordering = "one two".split()
    rdict.swap()
    assert rdict.ordering == "two one".split()
    rdict.swap()
    assert rdict.ordering == "one two".split()
