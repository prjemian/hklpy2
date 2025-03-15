"""
"no_op" solver for testing.

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
from ..blocks.reflection import Reflection
from .base import SolverBase

logger = logging.getLogger(__name__)


class NoOpSolver(SolverBase):
    """
    ``"no_op"`` (any OS) no transformations.

    |solver| that has no reciprocal space transformations.

    .. rubric:: Python Methods

    .. autosummary::

        ~addReflection
        ~calculate_UB
        ~extra_axis_names
        ~forward
        ~geometries
        ~inverse
        ~pseudo_axis_names
        ~real_axis_names
        ~refineLattice
        ~removeAllReflections

    .. rubric:: Python Properties

    .. autosummary::

        ~geometry
        ~lattice
        ~mode
        ~modes
        ~sample
    """

    name = "no_op"
    version = __version__

    def __init__(self, geometry: str, **kwargs) -> None:
        super().__init__(geometry, **kwargs)

    def addReflection(self, reflection: Reflection):
        pass

    def calculate_UB(self, r1, r2):
        return []

    @property
    def extra_axis_names(self):
        return []

    def forward(self, pseudos: dict) -> list[dict[str, float]]:
        return [{}]

    @classmethod
    def geometries(cls):
        return []

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

    def refineLattice(self, reflections: list[Reflection]) -> None:
        """No refinement."""
        return None

    def removeAllReflections(self):
        """Remove all reflections."""
        pass
