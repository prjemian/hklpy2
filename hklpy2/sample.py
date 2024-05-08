"""
A Crystalline Sample.

.. caution: work-in-progress

.. autosummary::

    ~Sample
    ~SampleError
"""

# TODO: When solver is needed, set it up first.

from . import Hklpy2Error
from . import Lattice
from . import ReflectionsDict
from . import SolverBase
from .misc import unique_name


class SampleError(Hklpy2Error):
    """Custom exceptions from the :mod:`hklpy2.sample` module."""


class Sample:
    """
    A crystalline sample mounted on a diffractometer.

    .. autosummary::

        ~name
        ~refine_lattice
        ~U
        ~UB
    """

    def __init__(self, solver: SolverBase, lattice: Lattice, name: str = None) -> None:
        self.name = name or unique_name()
        self.solver = solver
        self.lattice = lattice
        self.reflections = ReflectionsDict()

    @property
    def U(self):
        """Return the matrix, U, crystal orientation on the diffractometer."""
        return None  # TODO

    @property
    def UB(self):
        """
        Return the crystal orientation matrix, UB.

        * :math:`UB` - orientation matrix
        * :math:`B` - crystal lattice on the diffractometer
        * :math:`U` - rotation matrix, crystal orientation on diffractometer
        """
        # self.solver.calculateOrientation()  # TODO

    def refine_lattice(self):
        """Refine the lattice parameters from 3 or more reflections."""
        if len(self._reflections) < 3:
            raise SampleError("Need 3 or more reflections to refine lattice.")

        # self.solver.refineLattice()  # TODO

    # --------- get/set properties

    @property
    def lattice(self):
        """Sample crystal lattice."""
        return self._lattice

    @lattice.setter
    def lattice(self, lattice):
        if not isinstance(lattice, Lattice):
            raise TypeError(f"Must supply Lattice() object, received {lattice!r}")
        self._lattice = lattice

    @property
    def name(self):
        """Sample name."""
        return self._name

    @name.setter
    def name(self, new_name):
        if not isinstance(new_name, (type(None), str)):
            raise TypeError(f"Must supply str, received {new_name!r}")
        self._name = new_name

    @property
    def solver(self):
        """Diffractometer |solver|."""
        return self._solver

    @solver.setter
    def solver(self, new_solver):
        if not isinstance(new_solver, SolverBase):
            raise TypeError(f"Must supply SolverBase() object, received {new_solver!r}")
        # note: calling SolverBase() will always generate a TypeError
        # "Can't instantiate abstract class SolverBase with abstract methods" ...
        self._solver = new_solver
