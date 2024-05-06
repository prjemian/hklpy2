"""
Backend: no_op

no reciprocal-space conversions

.. autosummary::

    ~NoOpSolver
"""

from .. import __version__


class NoOpSolver:
    """
    A backend solver that has no transformations for reciprocal space.

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
        self._geometry = None

    def chooseGeometry(self, gname):
        """Select one of the diffractometer geometries."""
        self.gname = gname
        return None

    def forward(self):
        """Compute list of solutions(reals) from pseudos (hkl -> [angles])."""
        return []

    def getGeometries(self):
        """Ordered list of the geometry names."""
        return []

    def inverse(self):
        """Compute list of pseudoss from reals (angles -> hkl)."""
        return ["No Ops"]

    def pseudo_axis_names(self):
        """Ordered list of the pseudo axis names."""
        # such as h, k, l
        return []  # no axes

    def real_axis_names(self):
        """Ordered list of the real axis names."""
        # such as omega, chi, phi, tth
        return []  # no axes
