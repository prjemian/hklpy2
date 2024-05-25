"""
Backend: abstract base class

.. autosummary::

    ~SolverBase
"""

import logging
from abc import ABC
from abc import abstractmethod

from .. import __version__
from ..operations.lattice import Lattice
from ..operations.reflection import Reflection

logger = logging.getLogger(__name__)


class SolverBase(ABC):
    """
    Base class for all |hklpy2| |solver| classes.

    .. rubric:: Parameters

    * ``geometry``: (str) Name of geometry.
    * ``mode``: (str) Name of operating mode.  (default: current mode)

    Example::

        import hklpy2

        class MySolver(hklpy2.SolverBase):
            ...

    .. note:: :class:`~SolverBase`, an `abstract base
        class <https://docs.python.org/3/library/abc.html#abc.ABC>`_,
        cannot not be used directly by |hklpy2| users.

    As the parent class for all custom :index:`Solver` classes,
    :class:`~SolverBase` defines the methods and attributes to be written
    that will connect |hklpy2| with the support library that defines
    specific diffractometer geometries and the computations for
    using them.  Subclasses should implement each of these methods
    as best fits the underlying support library.

    .. seealso:: :ref:`api.solvers.hkl_soleil` & :ref:`api.solvers.no_op`

    .. rubric:: Python Methods

    .. autosummary::

        ~addReflection
        ~addSample
        ~calculateOrientation
        ~extra_axis_names
        ~forward
        ~geometries
        ~inverse
        ~pseudo_axis_names
        ~real_axis_names
        ~refineLattice

    .. rubric:: Python Properties

    .. autosummary::

        ~geometry
        ~lattice
        ~mode
        ~modes
    """

    name = "base"
    """Name of this Solver."""

    version = __version__
    """Version of this Solver."""

    def __init__(
        self,
        geometry: str,
        *,
        mode: str = "",  # "": accept solver's default mode
        **kwargs,
    ) -> None:
        self.geometry = geometry
        self.mode = mode

        logger.debug("geometry=%s, kwargs=%s", repr(geometry), repr(kwargs))

    def __repr__(self) -> str:
        # fmt: off
        args = [
            f"{s}={getattr(self, s)!r}"
            for s in "name version geometry".split()
        ]
        # fmt: on
        return f"{self.__class__.__name__}({', '.join(args)})"

    @abstractmethod
    def addReflection(self, pseudos, reals, wavelength):
        """Add coordinates of a diffraction condition (a reflection)."""

    @abstractmethod
    def addSample(self, sample):
        """Add a sample."""

    @abstractmethod
    def calculateOrientation(self, r1, r2):
        """Calculate the UB (orientation) matrix from two reflections."""

    @property
    @abstractmethod
    def extra_axis_names(self):
        """Ordered list of any extra axis names (such as x, y, z)."""
        # Do NOT sort.
        return []

    @abstractmethod
    def forward(self):
        """Compute list of solutions(reals) from pseudos (hkl -> [angles])."""
        # based on geometry and mode
        return [{}]

    @classmethod
    @abstractmethod
    def geometries(cls):
        """
        Ordered list of the geometry names.

        EXAMPLES::

            >>> from hklpy2 import get_solver
            >>> Solver = get_solver("no_op")
            >>> Solver.geometries()
            []
            >>> solver = Solver("TH TTH Q")
            >>> solver.geometries()
            []
        """
        return []

    @property
    @abstractmethod
    def geometry(self) -> str:
        """
        Name of selected diffractometer geometry.

        Cannot be changed once solver is created.  Instead, make a new solver
        for each geometry.
        """
        return self._geometry

    @geometry.setter
    @abstractmethod
    def geometry(self, value: str):
        self._geometry = value

    @abstractmethod
    def inverse(self, reals: dict):
        """Compute tuple of pseudos from reals (angles -> hkl)."""

    @property
    def lattice(self):
        """
        Crystal lattice parameters.  (Not used by this |solver|.)
        """
        return self._lattice

    @lattice.setter
    def lattice(self, value):
        if not isinstance(value, Lattice):
            raise TypeError(f"Must supply Lattice object, received {value!r}")
        self._lattice = value

    @property
    def mode(self):
        """
        Diffractometer geometry operation mode for :meth:`forward()`.

        A mode defines which axes will be modified by the
        :meth:`forward` computation.
        """
        try:
            self._mode
        except AttributeError:
            self._mode = ""
        return self._mode

    @mode.setter
    def mode(self, value):
        from .. import check_value_in_list  # avoid circular import here

        check_value_in_list("Mode", value, self.modes, blank_ok=True)
        self._mode = value

    @property
    @abstractmethod
    def modes(self):
        """List of the geometry operating modes."""
        return []

    @property
    @abstractmethod
    def pseudo_axis_names(self):
        """Ordered list of the pseudo axis names (such as h, k, l)."""
        # Do NOT sort.
        return []

    @property
    @abstractmethod
    def real_axis_names(self):
        """Ordered list of the real axis names (such as th, tth)."""
        # Do NOT sort.
        return []

    @abstractmethod
    def refineLattice(self, reflections: list[Reflection]) -> Lattice:
        """Refine the lattice parameters from a list of reflections."""
