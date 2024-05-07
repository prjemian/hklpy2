"""
Backend: abstract base class

.. autosummary::

    ~SolverBase
"""

from abc import ABC, abstractmethod

from .. import __version__


class SolverBase(ABC):
    """
    The base class for all |hklpy2| Solver classes.

    .. autosummary::

        ~chooseGeometry
        ~forward
        ~getGeometries
        ~inverse
        ~pseudo_axis_names
        ~real_axis_names
    """

    __version__ = __version__

    def __init__(self) -> None:
        self.gname = None

    @abstractmethod
    def chooseGeometry(self, gname, **kwargs):
        """Select one of the diffractometer geometries."""
        pass

    @abstractmethod
    def forward(self):
        """Compute list of solutions(reals) from pseudos (hkl -> [angles])."""
        pass

    @abstractmethod
    def getGeometries(self):
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
