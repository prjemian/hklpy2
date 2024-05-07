"""
Backend: Hkl

.. autosummary::

    ~HklSolver

:home: https://people.debian.org/~picca/hkl/hkl.html
:source: https://repo.or.cz/hkl.git
"""

import gi

gi.require_version("Hkl", "5.0")

from gi.repository import GLib  # noqa: E402, F401
from gi.repository import Hkl as libhkl  # noqa: E402

from .abstract_solver import SolverBase


class HklSolver(SolverBase):
    """
    This solver wraps the Hkl (libhkl) library from Fred Picca (Soleil).

    .. autosummary::

        ~chooseGeometry
        ~forward
        ~getGeometries
        ~inverse
        ~pseudo_axis_names
        ~real_axis_names
    """

    __version__ = libhkl.VERSION

    def __init__(self) -> None:
        self.gname = None

        self.detector = libhkl.Detector.factory_new(libhkl.DetectorType(0))
        self._engine = None
        self._engines = None
        self._factories = libhkl.factories()
        self._geometry = None
        self.user_units = libhkl.UnitEnum.USER

    def chooseGeometry(self, gname, engine="hkl"):
        """Select one of the diffractometer geometries."""
        factory = self._factories[gname]
        self.gname = gname
        self._geometry = factory.create_new_geometry()
        self._engines = factory.create_new_engine_list()
        self._engine = self._engines.engine_get_by_name(engine)
        return self._geometry

    def forward(self):
        """Compute list of solutions(reals) from pseudos (hkl -> [angles])."""
        return []  # TODO

    def getGeometries(self):
        """Ordered list of the geometry names."""
        geometries = [
            f"{factory.name_get()}, {engine.name_get()}"
            # f"{factory.name_get()}"
            for factory in (self._factories or {}).values()
            for engine in (self._engines or {}).engines_get()
        ]
        return sorted(set(geometries))

    def inverse(self):
        """Compute tuple of pseudos from reals (angles -> hkl)."""
        return tuple()  # TODO

    def pseudo_axis_names(self):
        """Ordered list of the pseudo axis names."""
        # such as h, k, l
        if self._engine is not None:
            return self._engine.pseudo_axis_names_get()

    def real_axis_names(self):
        """Ordered list of the real axis names."""
        # such as omega, chi, phi, tth
        if self._geometry is not None:
            return self._geometry.axis_names_get()
