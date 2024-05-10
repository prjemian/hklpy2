from math import pi

from .. import Lattice
from .. import Reflection
from .. import Sample
from .. import get_solver
from .. import solvers
from . import NO_OP_SOLVER_TYPE_STR


def test_as_in_demo_notebook():
    solver_name = "no_op"
    assert solver_name in solvers()

    SolverClass = get_solver(solver_name)
    assert SolverClass is not None
    assert SolverClass.__class__.__name__ == "ABCMeta"  # abstract base metaclass

    solver = SolverClass()
    assert f"{solver!r}" == f"NoOpSolver(name='no_op', version='{solver.__version__}')"
    assert str(type(solver)) == NO_OP_SOLVER_TYPE_STR
    assert solver.geometry is None, f"{solver.geometry=}"

    gname = "anything"
    solver.geometry = gname
    assert solver.geometry == gname, f"{solver.geometry=}"
    assert len(solver.pseudo_axis_names) == 0, f"{solver.pseudo_axis_names=!r}"
    assert len(solver.real_axis_names) == 0, f"{solver.real_axis_names=!r}"

    vibranium_lattice = Lattice(2 * pi)
    assert vibranium_lattice is not None
    assert vibranium_lattice.a == 2 * pi
    assert vibranium_lattice.a == vibranium_lattice.b
    assert vibranium_lattice.a == vibranium_lattice.c
    assert vibranium_lattice.alpha == 90
    assert vibranium_lattice.alpha == vibranium_lattice.beta
    assert vibranium_lattice.alpha == vibranium_lattice.gamma

    vibranium = Sample(solver, vibranium_lattice, name="vibranium")
    assert vibranium is not None
    assert vibranium.name == "vibranium"
    assert "a=6.2832, b=6.2832, c=6.2832," in str(vibranium)

    vibranium_lattice.digits = 2
    assert "a=6.28, b=6.28, c=6.28," in str(vibranium)

    assert vibranium.reflections.ordering == []

    # define two reflections
    vibranium.reflections.add(
        Reflection(
            solver,
            dict(h=1, k=0, l=0),
            dict(omega=10, chi=0, phi=0, tth=20),
            wavelength=1.00,
            name="r1",
        )
    )
    assert vibranium.reflections["r1"] is not None
    assert vibranium.reflections["r1"].name == "r1"

    vibranium.reflections.add(
        Reflection(
            solver,
            dict(h=0, k=1, l=0),
            dict(omega=10, chi=-90, phi=0, tth=20),
            wavelength=1.00,
            name="r2",
        )
    )
    assert vibranium.reflections["r2"] is not None
    assert vibranium.reflections["r2"].name == "r2"
    assert vibranium.reflections.ordering == "r1 r2".split()

    # swap the two reflections
    vibranium.reflections.swap()
    assert vibranium.reflections.ordering == "r2 r1".split()
