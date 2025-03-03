"""
A Crystalline Sample.

.. autosummary::

    ~Sample
    ~SampleError
"""

import logging

from .lattice import Lattice
from .misc import SampleError
from .misc import unique_name
from .reflection import ReflectionsDict

logger = logging.getLogger(__name__)


class Sample:
    """
    A crystalline sample mounted on a diffractometer.

    .. note:: Internal use only.

    .. rubric:: Python Methods

    .. autosummary::

        ~refine_lattice

    .. rubric:: Python Properties

    .. autosummary::

        ~_asdict
        ~lattice
        ~name
        ~reflections
        ~remove_reflection
        ~U
        ~UB
    """

    def __init__(
        self,
        operator,
        name: str,
        lattice: Lattice,
    ) -> None:
        from ..ops import Operations
        from .misc import IDENTITY_MATRIX_3X3

        if not isinstance(operator, Operations):
            raise TypeError(f"Unexpected type {operator=!r}, expected Operations")
        self.name = name or unique_name()
        self.operator = operator
        self.lattice = lattice
        self.U = IDENTITY_MATRIX_3X3
        self.UB = IDENTITY_MATRIX_3X3
        # TODO: reciprocal_lattice
        self.reflections = ReflectionsDict()

    def __repr__(self):
        """Brief text representation."""
        return f"Sample(name={self.name!r}, lattice={self.lattice!r})"

    def _asdict(self):
        """Describe the sample as a dictionary."""
        return {
            "name": self.name,
            "lattice": self.lattice._asdict(),
            "reflections": self.reflections._asdict(),
            "reflections_order": self.reflections.order,
            "U": self.U,
            "UB": self.UB,
            "digits": self.digits,
        }

    def _fromdict(self, config, operator=None):
        """Redefine sample from a (configuration) dictionary."""
        self.name = config["name"]
        self.digits = config["digits"]
        self.lattice._fromdict(config["lattice"])
        self.reflections._fromdict(config["reflections"], operator=operator)
        self.reflections.order = config["reflections_order"]
        self.U = config["U"]
        self.UB = config["UB"]

    def refine_lattice(self):
        """Refine the lattice parameters from 3 or more reflections."""
        if len(self.reflections) < 3:
            raise SampleError("Need 3 or more reflections to refine lattice.")

        # self.operator.refineLattice()  # TODO: #40

    def remove_reflection(self, name: str) -> None:
        """Remove the named reflection."""
        if name not in self.reflections:
            raise KeyError(f"Reflection {name!r} is not found.")
        self.reflections.pop(name)
        if name in self.reflections.order:
            self.reflections.order.remove(name)

    # --------- get/set properties

    @property
    def digits(self):
        """Sample crystal lattice."""
        return self.lattice.digits

    @digits.setter
    def digits(self, value):
        self.lattice.digits = value

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
    def U(self) -> list[list[float]]:
        """Return the matrix, U, crystal orientation on the diffractometer."""
        return self._U

    @U.setter
    def U(self, value: list[list[float]]):
        self._U = value

    @property
    def UB(self) -> list[list[float]]:
        """
        Return the crystal orientation matrix, UB.

        * :math:`UB` - orientation matrix
        * :math:`B` - crystal lattice on the diffractometer
        * :math:`U` - rotation matrix, relative orientation of crystal on diffractometer
        """
        return self._UB

    @UB.setter
    def UB(self, value: list[list[float]]):
        # TODO: #41 validate
        self._UB = value
