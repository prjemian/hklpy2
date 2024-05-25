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
from ..operations.lattice import Lattice
from ..operations.reflection import Reflection

try:
    import gi
except ModuleNotFoundError:
    raise SolverError("No gobject-introspection library.  Is libhkl installed?")

gi.require_version("Hkl", "5.0")

from gi.repository import GLib  # noqa: E402, F401, W0611
from gi.repository import Hkl as libhkl  # noqa: E402

logger = logging.getLogger(__name__)

AXES_READ = 0
AXES_WRITTEN = 1


class HklSolver(SolverBase):
    """
    ``"hkl_soleil"`` (Linux x86_64 only) |libhkl|.

    Wraps the |libhkl| library, written by Frédéric-Emmanuel PICCA (Soleil),
    with support for many common diffractometer geometries.

    .. rubric:: Parameters

    * geometry: (str) Name of geometry.
    * engine: (str) Name of computation engine.  (default: ``"hkl"``)
    * mode: (str) Name of operating mode.  (default: current mode)
    * pseudos: ([PseudoPositioner]) List of pseudo positioners.
      (default: ``[]``)
    * reals: ([PositionerBase]) List of real positioners.
      (default: ``[]``)
    * extra: ([PseudoPositioner]+[PositionerBase) List of extra positioners.
      (default: ``[]``)
      First the pseudos, then the reals.

    .. note:: The lists of ``pseudos``, ``reals``, and ``extras`` are the
       corresponding axes of the diffractometer, in the order expected by
       the |solver| geometry.  The names can be different between the
       supplied and expected axes.  They are matched by order in the list.

    .. rubric:: Python Methods

    .. autosummary::

        ~addReflection
        ~addSample
        ~calculateOrientation
        ~forward
        ~geometries
        ~inverse
        ~refineLattice

    .. rubric:: Python Properties

    .. autosummary::

        ~axes_c
        ~axes_r
        ~axes_w
        ~engine
        ~engines
        ~extra_axis_names
        ~geometry
        ~lattice
        ~mode
        ~modes
        ~pseudo_axis_names
        ~real_axis_names
    """

    name = "hkl_soleil"
    version = libhkl.VERSION

    def __init__(
        self,
        geometry: str,
        *,
        engine="hkl",
        mode="",
        **kwargs,
    ) -> None:
        self._engine = None
        self._gname_locked = False  # can't chanmge after setting once

        super().__init__(geometry, **kwargs)

        # note: must keep the 'engines' object as class attribute or
        # random core dumps, usually when accessing 'engine.name_get()'.
        self._factory = libhkl.factories()[geometry]
        self._engines = self._factory.create_new_engine_list()  # note!
        self._engine = self._engines.engine_get_by_name(engine)
        self._geometry = self._factory.create_new_geometry()

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

    @property
    def axes_c(self):
        """
        HKL real axis names.

        Held constant during 'forward()' computation.
        """
        # Do NOT sort.
        return [axis for axis in self.axes_r if axis not in self.axes_w]

    @property
    def axes_r(self):
        """HKL real axis names (read-only)."""
        return self._engine.axis_names_get(AXES_READ)  # Do NOT sort.

    @property
    def axes_w(self):
        """
        HKL real axis names.

                Updated by 'forward()' computation.
        """
        return self._engine.axis_names_get(AXES_WRITTEN)  # Do NOT sort.

    def calculateOrientation(self, r1, r2):  # TODO
        """Calculate the UB (orientation) matrix from two reflections."""
        raise NotImplementedError()

    @property
    def engine(self):
        """Selected computational engine for this geometry."""
        return self._engine.name_get()

    @property
    def engines(self):
        """List of the computational engines available in this geometry."""
        return [engine.name_get() for engine in self._engines.engines_get()]

    @property
    def extra_axis_names(self):
        """
        Ordered list of any extra axis names (such as x, y, z).

        Depends on selected geometry, engine, and mode.
        """
        return self._engine.parameters_names_get()  # Do NOT sort.

    def forward(self):  # TODO:
        """Compute list of solutions(reals) from pseudos (hkl -> [angles])."""
        logger.debug("(%r) forward()", __name__)
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

    def inverse(self, reals: dict):  # TODO
        """Compute tuple of pseudos from reals (angles -> hkl)."""
        logger.debug("{__name__=} inverse(reals=%r)", reals)
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
        return self._engine.pseudo_axis_names_get()  # Do NOT sort.

    @property
    def real_axis_names(self):
        """Ordered list of the real axis names (such as th, tth)."""
        return self._geometry.axis_names_get()  # Do NOT sort.

    def refineLattice(self, reflections: list[Reflection]) -> Lattice:
        """Refine the lattice parameters from a list of reflections."""
        raise NotImplementedError()  # TODO:
