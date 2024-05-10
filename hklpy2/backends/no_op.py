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
        ~geometry
        ~inverse
        ~lattice
        ~mode
        ~modes
        ~pseudo_axis_names
        ~real_axis_names
        ~refineLattice
    """

    __name__ = "no_op"
    __version__ = __version__

    def __init__(self) -> None:
        super().__init__()
        self._geometry = None

    def addReflection(self, pseudos, reals, wavelength):
        pass  # TODO

    def addSample(self, sample):
        pass  # TODO

    def calculateOrientation(self, r1, r2):
        return

    def forward(self):
        return [{}]

    @property
    def geometries(self):
        return []

    @property
    def geometry(self):
        """Diffractometer geometry."""
        return self._geometry

    @geometry.setter
    def geometry(self, value):
        if not isinstance(value, (type(None), str)):
            raise TypeError(f"Must supply str, received {value!r}")
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
        pass  # TODO
