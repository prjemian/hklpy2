"""
Backend: Hkl (``"hkl_soleil"``)

Example::

    >>> import hklpy2
    >>> SolverClass = hklpy2.get_solver("hkl_soleil")
    >>> libhkl_solver = SolverClass(geometry="E4CV")
    >>> solver
    HklSolver(name='hkl_soleil', version='v5.0.0.3434', geometry='E4CV', engine='hkl', mode='bissector')

.. autosummary::

    ~HklSolver
"""

import logging

from .. import SolverBase
from .. import SolverError
from .. import check_value_in_list

try:
    import gi
except ModuleNotFoundError:
    raise SolverError("No gobject-introspection library.  Is libhkl installed?")

gi.require_version("Hkl", "5.0")

from gi.repository import GLib  # noqa: E402, F401, W0611
from gi.repository import Hkl as libhkl  # noqa: E402

logger = logging.getLogger(__name__)


class HklSolver(SolverBase):
    """
    ``"hkl_soleil"`` (Linux x86_64 only) |libhkl|.

    |solver| with support for many common diffractometer geoemtries.
    Wraps the |libhkl| library from Frédéric-Emmanuel PICCA (Soleil).

    .. rubric:: Python Methods

    .. autosummary::

        ~addReflection
        ~addSample
        ~calculateOrientation
        ~forward
        ~inverse
        ~refineLattice

    .. rubric:: Python Properties

    .. autosummary::

        ~engine
        ~engines
        ~extra_axis_names
        ~geometries
        ~geometry
        ~geometry_engine
        ~lattice
        ~mode
        ~modes
        ~pseudo_axis_names
        ~real_axis_names
    """

    name = "hkl_soleil"
    version = libhkl.VERSION

    def __init__(self, *, geometry: str, engine="hkl", mode="", **kwargs) -> None:
        self._engine = None
        self._gname_locked = False  # can't chanmge after setting once

        super().__init__(geometry=geometry, **kwargs)
        self.geometry_engine = geometry, engine

        # self.print_info_DEVELOPER()

    def print_info_DEVELOPER(self):
        print(f"{self=!r}")
        print(f"{self.name=!r}")
        print(f"{self.__class__.__name__=!r}")
        print(f"{self.version=!r}")
        print(f"{self._factory=!r}")
        print(f"{self._geometry=!r}")
        print(f"{self.geometry=!r}")
        print(f"{self.engines=!r}")
        print(f"{self._engines=!r}")
        print(f"{self._engine=!r}")
        print(f"{self.engine=!r}")
        print(f"{self.modes=!r}")
        print(f"{self.mode=!r}")
        print(f"{self.pseudo_axis_names=!r}")
        print(f"{self.real_axis_names=!r}")
        print(f"{self.extra_axis_names=!r}")
        print(f"{self.user_pseudos=!r}")
        print(f"{self.user_reals=!r}")
        print(f"{self.user_extras=!r}")

    def __repr__(self):
        args = [
            f"{s}={getattr(self, s)!r}"
            for s in "name version geometry engine mode".split()
        ]
        return f"{self.__class__.__name__}({', '.join(args)})"

    def addReflection(self, pseudos, reals, wavelength):  # TODO
        """Add coordinates of a diffraction condition (a reflection)."""
        raise NotImplementedError()

    def addSample(self, sample):  # TODO
        """Add a sample."""
        raise NotImplementedError()

    def calculateOrientation(self, r1, r2):  # TODO
        """Calculate the UB (orientation) matrix from two reflections."""
        raise NotImplementedError()

    @property
    def engine(self):
        """Selected computational engine for this geometry."""
        if self._engine is None:
            return ""
        return self._engine.name_get()

    @property
    def engines(self):
        """List of the computational engines available in this geometry."""
        if self._engines is None:
            return []
        return [engine.name_get() for engine in self._engines.engines_get()]

    @property
    def extra_axis_names(self):
        """
        Ordered list of any extra axis names (such as x, y, z).

        Depends on selected geometry, engine, and mode.
        """
        # Do NOT sort.
        return self._engine.parameters_names_get()

    def forward(self):  # TODO:
        """Compute list of solutions(reals) from pseudos (hkl -> [angles])."""
        print(f"{__name__=} forward()")
        return [{}]

    @classmethod
    def geometries(cls):
        return sorted(libhkl.factories())

    @property
    def geometry(self) -> str:
        return self._gname

    @geometry.setter
    def geometry(self, value: str):
        if self._gname_locked:
            raise SolverError(f"Geometry {self._gname} cannot be changed.")
        check_value_in_list("Geometry", value, self.geometries())
        self._gname = value
        self._gname_locked = True

    @property
    def geometry_engine(self):
        """Library objects for geometry & computation engine."""
        return self._geometry, self._engine

    @geometry_engine.setter
    def geometry_engine(self, values):
        # note: must keep the 'engines' object as class attribute or
        # random core dumps, usually when accessing 'engine.name_get()'.

        gname, ename = values
        self._factory = libhkl.factories()[gname]
        self._engines = self._factory.create_new_engine_list()  # note!
        self._engine = self._engines.engine_get_by_name(ename)
        self._geometry = self._factory.create_new_geometry()

    def inverse(self, reals: dict):  # TODO
        """Compute tuple of pseudos from reals (angles -> hkl)."""
        print(f"{__name__=} inverse({reals=!r})")
        return tuple(0, 0, 0)

    @property
    def modes(self):
        """List of the geometry operating modes."""
        if self._engine is None:
            return []
        return self._engine.modes_names_get()

    @property
    def mode(self):
        """Name of the current geometry operating mode."""
        if self._engine is None:
            return []
        return self._engine.current_mode_get()

    @mode.setter
    def mode(self, value):
        check_value_in_list("Mode", value, self.modes, blank_ok=True)
        if value == "":
            return  # keep current mode
        self._engine.current_mode_set(value)

    @property
    def pseudo_axis_names(self):
        """Ordered list of the pseudo axis names (such as h, k, l)."""
        # Do NOT sort.
        return self._engine.pseudo_axis_names_get()

    @property
    def real_axis_names(self):
        """Ordered list of the real axis names (such as th, tth)."""
        # Do NOT sort.
        return self._geometry.axis_names_get()

    def refineLattice(self, reflections):  # TODO
        """Refine the lattice parameters from a list of reflections."""
        raise NotImplementedError()
