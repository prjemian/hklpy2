"""
Backend: abstract base class

.. autosummary::

    ~SolverBase
"""

from abc import ABC
from abc import abstractmethod

from .. import __version__

SOLVER_ENTRYPOINT_GROUP = "hklpy2.solver"
"""Name by which hklpy2 backend Solver classes are grouped."""


def setSolver(solver_name):
    """Load a Solver class from a named entry point."""
    from importlib.metadata import entry_points

    entries = entry_points(group=SOLVER_ENTRYPOINT_GROUP)
    return entries[solver_name].load()


def solvers():
    """Dictionary of available Solver classes by entry point name."""
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
    Base class for all |hklpy2| Solver classes.

    .. autosummary::

        ~forward
        ~geometries
        ~inverse
        ~pseudo_axis_names
        ~real_axis_names
        ~setGeometry
    """

    __version__ = __version__

    def __init__(self) -> None:
        self.gname = None

    @abstractmethod
    def forward(self):
        """Compute list of solutions(reals) from pseudos (hkl -> [angles])."""
        pass

    @abstractmethod
    def geometries(self):
        """Ordered list of the geometry names."""
        pass

    @abstractmethod
    def inverse(self):
        """Compute tuple of pseudos from reals (angles -> hkl)."""
        pass

    @abstractmethod
    def pseudo_axis_names(self):
        """Ordered list of the pseudo axis names."""
        # such as h, k, l
        pass

    @abstractmethod
    def real_axis_names(self):
        """Ordered list of the real axis names."""
        # such as omega, chi, phi, tth
        pass

    @abstractmethod
    def setGeometry(self, gname, **kwargs):
        """Select one of the diffractometer geometries."""
        pass
