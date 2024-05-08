"""
Backend: abstract base class

.. autosummary::

    ~SolverBase
    ~SOLVER_ENTRYPOINT_GROUP
    ~get_solver
    ~solvers
"""

from abc import ABC
from abc import abstractmethod

from .. import __version__

SOLVER_ENTRYPOINT_GROUP = "hklpy2.solver"
"""Name by which |hklpy2| backend |solver| classes are grouped."""


def get_solver(solver_name):
    """
    Load a Solver class from a named entry point.

    ::

        import hklpy2
        Solver = hklpy2.get_solver("hkl_soleil")
    """
    from importlib.metadata import entry_points

    entries = entry_points(group=SOLVER_ENTRYPOINT_GROUP)
    return entries[solver_name].load()


def solvers():
    """
    Dictionary of available Solver classes, mapped by entry point name.

    ::

        import hklpy2
        print(hklpy2.solvers())
    """
    from importlib.metadata import entry_points

    # fmt: off
    entries = {
        ep.name: ep.value
        for ep in entry_points(group=SOLVER_ENTRYPOINT_GROUP)
    }
    # fmt: on
    return entries


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

    .. autosummary::

        ~addReflection
        ~addSample
        ~calculateOrientation
        ~forward
        ~geometries
        ~inverse
        ~modes
        ~pseudo_axis_names
        ~real_axis_names
        ~refineLattice
        ~setGeometry
        ~setLattice
        ~setMode
    """

    __version__ = __version__
    """Version of this Solver."""

    def __init__(self) -> None:
        self.gname = None

    @abstractmethod
    def addReflection(self, pseudos, reals, wavelength):
        """Add information about a reflection."""
        pass

    @abstractmethod
    def addSample(self, sample):
        """Add a sample."""
        pass

    @abstractmethod
    def calculateOrientation(self, r1, r2):
        """Calculate the UB (orientation) matrix from two reflections."""
        pass

    @abstractmethod
    def forward(self):
        """Compute list of solutions(reals) from pseudos (hkl -> [angles])."""
        pass

    @property
    @abstractmethod
    def geometries(self):
        """Ordered list of the geometry names."""
        pass

    @abstractmethod
    def inverse(self):
        """Compute tuple of pseudos from reals (angles -> hkl)."""
        pass

    @property
    @abstractmethod
    def modes(self):
        """List of the geometry operating modes."""
        pass

    @property
    @abstractmethod
    def pseudo_axis_names(self):
        """Ordered list of the pseudo axis names (such as h, k, l)."""
        pass

    @property
    @abstractmethod
    def real_axis_names(self):
        """Ordered list of the real axis names (such as th, tth)."""
        pass

    @abstractmethod
    def refineLattice(self, reflections):
        """Refine the lattice parameters from a list of reflections."""
        pass

    @abstractmethod
    def setGeometry(self, gname, **kwargs):
        """Select one of the diffractometer geometries."""
        pass

    @abstractmethod
    def setLattice(self, lattice):
        """Define the sample's lattice parameters."""
        pass

    @abstractmethod
    def setMode(self, mode):
        """
        Define the geometry's operating mode.

        A mode defines constraints on the solutions provided by the
        :meth:`forward` computation.
        """
        pass
