from ..misc import unique_name
from ..reflection import Reflection


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
