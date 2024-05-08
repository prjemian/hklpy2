"""
A Crystalline Sample.

.. caution: work-in-progress

.. autosummary::

    ~Sample
    ~SampleError
"""

# TODO: When solver is needed, set it up first.

from . import Hklpy2Error
from . import ReflectionsDict
from .misc import uuid7


class SampleError(Hklpy2Error):
    """Any exception from the :mod:`hklpy2.sample` module."""


class Sample:
    """
    A crystalline sample mounted on a diffractometer.

    .. autosummary::

        ~name
        ~refine_lattice
        ~U
        ~UB
    """

    def __init__(self, solver, lattice, name=None) -> None:
        self.name = name or uuid7()
        self.solver = solver
        self._lattice = lattice
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
            # fmt: off
            raise SampleError(
                "Must have at least 3 reflections to refine_lattice()."
            )
            # fmt: on

        # self.solver.refineLattice()  # TODO

    # --------- get/set properties

    @property
    def name(self):
        """Sample name."""
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name
