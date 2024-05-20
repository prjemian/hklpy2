"""
Backend: abstract base class

.. autosummary::

    ~SolverBase
"""

import logging
from abc import ABC
from abc import abstractmethod

from .. import __version__

logger = logging.getLogger(__name__)


class SolverBase(ABC):
    """
    Base class for all |hklpy2| |solver| classes.

    ::

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

    .. seealso:: :ref:`api.backends.hkl_soleil` & :ref:`api.backends.no_op`

    .. rubric:: Python Methods

    .. autosummary::

        ~addReflection
        ~addSample
        ~calculateOrientation
        ~extra_axis_names
        ~forward
        ~inverse
        ~pseudo_axis_names
        ~real_axis_names
        ~refineLattice

    .. rubric:: Python Properties

    .. autosummary::

        ~geometries
        ~geometry
        ~lattice
        ~mode
        ~modes
    """

    __name__ = "base"
    """Name of this Solver."""

    __version__ = __version__
    """Version of this Solver."""

    def __init__(
        self,
        geometry: str = None,
        pseudos: list = [],
        reals: list = [],
        extras: list = [],
        **kwargs,
    ) -> None:
        self.geometry = geometry

        self.user_pseudos = pseudos
        self.user_reals = reals
        self.user_extras = extras

        logger.debug(
            "geometry=%s, pseudos=%s, reals=%s, extras=%s, kwargs=%s",
            repr(geometry),
            repr(pseudos),
            repr(reals),
            repr(extras),
            repr(kwargs),
        )

    def __repr__(self) -> str:
        # fmt: off
        args = [
            f"{s}={getattr(self, f'__{s}__')!r}"
            for s in "name version".split()
        ]
        args.append(f"geometry={self.geometry!r}")
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
        return []

    @abstractmethod
    def forward(self):
        """Compute list of solutions(reals) from pseudos (hkl -> [angles])."""
        # based on geometry and mode
        return [{}]

    @property
    @abstractmethod
    def geometries(self):
        """Ordered list of the geometry names."""
        return []

    @property
    @abstractmethod
    def geometry(self):
        """Selected diffractometer geometry."""
        return self._geometry

    @geometry.setter
    @abstractmethod
    def geometry(self, value):
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
        from .. import Lattice

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
            self._mode = None
        return self._mode

    @mode.setter
    def mode(self, value):
        if not isinstance(value, (type(None), str)):
            raise TypeError(f"Must supply str, received {value!r}")
        if value not in self.modes:
            raise KeyError(f"Mode {value} unknown. Pick one of: {self.modes!r}")
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
        return []

    @property
    @abstractmethod
    def real_axis_names(self):
        """Ordered list of the real axis names (such as th, tth)."""
        return []

    @abstractmethod
    def refineLattice(self, reflections):
        """Refine the lattice parameters from a list of reflections."""
