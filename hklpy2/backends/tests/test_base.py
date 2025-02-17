"""Test the solver base class."""

# Many features are tested, albeit indrectly, in specific solvers.

from ...operations.lattice import Lattice
from ...operations.misc import IDENTITY_MATRIX_3X3
from ...operations.reflection import Reflection
from ..base import SolverBase


class TrivialSolver(SolverBase):
    """Trivial implementation for testing."""

    def addReflection(self, reflection: Reflection):
        """."""

    def calculate_UB(
        self,
        r1: Reflection,
        r2: Reflection,
    ) -> list[list[float]]:
        """."""
        return IDENTITY_MATRIX_3X3

    @property
    def extra_axis_names(self) -> list[str]:
        """."""
        return []

    def forward(self, pseudos: dict) -> list[dict[str, float]]:
        """."""
        return [{}]

    @classmethod
    def geometries(cls) -> list[str]:
        """."""
        return []

    @property
    def geometry(self) -> str:
        """."""
        return self._geometry

    @geometry.setter
    def geometry(self, value: str):
        self._geometry = value

    def inverse(self, reals: dict) -> dict[str, float]:
        """."""
        return {}

    @property
    def modes(self) -> list[str]:
        """."""
        return []

    @property
    def pseudo_axis_names(self) -> list[str]:
        """Ordered list of the pseudo axis names (such as h, k, l)."""
        # Do NOT sort.
        return []

    @property
    def real_axis_names(self) -> list[str]:
        """Ordered list of the real axis names (such as th, tth)."""
        # Do NOT sort.
        return []

    def refineLattice(self, reflections: list[Reflection]) -> Lattice:
        """Refine the lattice parameters from a list of reflections."""
        return Lattice(1.0)  # always cubic, for testing

    def removeAllReflections(self) -> None:
        """Remove all reflections."""


def test_SolverBase_extras():
    solver = TrivialSolver("test_geo")
    assert isinstance(solver, SolverBase)
    assert solver.name == "base"
    assert solver.extra_axis_names == [], f"{solver.extra_axis_names=}"
    assert solver.extras == {}, f"{solver.extras=}"

    md = solver._metadata
    assert isinstance(md, dict)
    expected = {
        "name": solver.name,
        "description": repr(solver),
        "geometry": solver.geometry,
        "real_axes": solver.real_axis_names,
        "version": solver.version,
    }
    assert md == expected
