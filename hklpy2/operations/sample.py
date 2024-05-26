"""
A Crystalline Sample.

.. caution: work-in-progress

.. autosummary::

    ~Sample
    ~SampleError
"""

import logging

from .. import Hklpy2Error
from .lattice import Lattice
from .misc import unique_name
from .reflection import ReflectionsDict

logger = logging.getLogger(__name__)


class SampleError(Hklpy2Error):
    """Custom exceptions from the :mod:`hklpy2.operations.sample` module."""


class Sample:
    """
    A crystalline sample mounted on a diffractometer.

    .. note:: Internal use only.

    .. rubric:: Python Methods

    .. autosummary::

        ~refine_lattice

    .. rubric:: Python Properties

    .. autosummary::

        ~lattice
        ~name
        ~reflections
        ~U
        ~UB
    """

    def __init__(
        self,
        operator,
        name: str,
        lattice: Lattice,
    ) -> None:
        from ..ops import SolverOperator

        if not isinstance(operator, SolverOperator):
            raise TypeError(f"Unexpected type {operator=!r}, expected SolverOperator")
        self.name = name or unique_name()
        self.operator = operator
        self.lattice = lattice
        # TODO: reciprocal_lattice
        self.reflections = ReflectionsDict()

    def __repr__(self):
        return f"Sample(name={self.name!r}, lattice={self.lattice!r})"

    def refine_lattice(self):
        """Refine the lattice parameters from 3 or more reflections."""
        if len(self.reflections) < 3:
            raise SampleError("Need 3 or more reflections to refine lattice.")

        # self.operator.refineLattice()  # TODO

    # --------- get/set properties

    @property
    def lattice(self):
        """Sample crystal lattice."""
        return self._lattice

    @lattice.setter
    def lattice(self, value):
        if not isinstance(value, Lattice):
            raise TypeError(f"Must supply Lattice() object, received {value!r}")
        self._lattice = value

    @property
    def name(self):
        """Sample name."""
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, (type(None), str)):
            raise TypeError(f"Must supply str, received {value!r}")
        self._name = value

    @property
    def reflections(self):
        """Ordered dictionary of orientation reflections."""
        return self._reflections

    @reflections.setter
    def reflections(self, value):
        if not isinstance(value, ReflectionsDict):
            raise TypeError(f"Must supply ReflectionsDict() object, received {value!r}")
        self._reflections = value

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
        * :math:`U` - rotation matrix, relative orientation of crystal on diffractometer
        """
        # self.operator.calculateOrientation()  # TODO
