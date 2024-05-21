"""
Backend: no_op (``"no_op"``)

no reciprocal-space conversions

Example::

    import hklpy2
    SolverClass = hklpy2.get_solver("no_op")
    noop_solver = SolverClass()

.. autosummary::

    ~NoOpSolver
"""

import logging

from .. import __version__
from .base import SolverBase

logger = logging.getLogger(__name__)


class NoOpSolver(SolverBase):
    """
    ``"no_op"`` (any OS) no transformations.

    |solver| that has no reciprocal space transformations.

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

    name = "no_op"
    version = __version__

    def __init__(self, *, geometry: str, **kwargs) -> None:
        super().__init__(geometry=geometry, **kwargs)

    def addReflection(self, pseudos, reals, wavelength):
        pass

    def addSample(self, sample):
        pass

    def calculateOrientation(self, r1, r2):
        return

    @property
    def extra_axis_names(self):
        return []

    def forward(self):
        return [{}]

    @classmethod
    def geometries(cls):
        return []

    @property
    def geometry(self) -> str:
        """Diffractometer geometry."""
        return self._geometry

    @geometry.setter
    def geometry(self, value: str):
        self._geometry = value

    def inverse(self, reals: dict):
        return {}

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

    def setLattice(self, lattice):
        pass
