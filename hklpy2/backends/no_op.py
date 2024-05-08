"""
Backend: no_op

no reciprocal-space conversions

.. autosummary::

    ~NoOpSolver
"""

from .. import __version__
from .base import SolverBase


class NoOpSolver(SolverBase):
    """
    ``"no_op"`` (any OS) no transformations.

    |solver| that has no reciprocal space transformations.

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

    def __init__(self) -> None:
        self.gname = None
        self._geometry = None

    def addReflection(self, pseudos, reals, wavelength):
        pass  # TODO

    def addSample(self, sample):
        pass  # TODO

    def calculateOrientation(self, r1, r2):
        return

    def forward(self):
        return []

    @property
    def geometries(self):
        return []

    def inverse(self):
        return ["No Ops"]

    @property
    def modes(self):
        return []

    @property
    def pseudo_axis_names(self):
        return []  # no axes

    @property
    def real_axis_names(self):
        return []  # no axes

    def refineLattice(self, reflections):
        return None

    def setGeometry(self, gname, **kwargs):
        self.gname = gname
        return None

    def setLattice(self, lattice):
        pass  # TODO

    def setMode(self, mode):
        pass
