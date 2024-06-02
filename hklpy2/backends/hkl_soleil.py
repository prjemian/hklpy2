"""
Backend: Hkl (``"hkl_soleil"``)

..  caution:: The ``hkl_soleil`` |solver| is not available
    for Windows or Mac OS.  The underlying |libhkl| support 
    library is only provided
    for Linux 64-bit OS at this time.

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
import math
import platform

from .. import SolverBase
from .. import SolverError
from .. import check_value_in_list
from ..operations.lattice import Lattice
from ..operations.misc import unique_name
from ..operations.reflection import Reflection
from ..operations.sample import Sample
from .base import IDENTITY_MATRIX_3X3

if platform.system() != "Linux":
    raise SolverError("'hkl_soleil' only available for linux 64-bit.")
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
LIBHKL_DETECTOR_TYPE = 0
LIBHKL_UNITS = {
    "default": libhkl.UnitEnum.DEFAULT,
    "user": libhkl.UnitEnum.USER,
}
LIBHKL_USER_UNITS = LIBHKL_UNITS["user"]
ROUNDOFF_DIGITS = 9

def _roundoff(values, digits=ROUNDOFF_DIGITS):
    """Prevent underflows and '-0'."""
    return [round(v, digits) or 0 for v in values]


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
        ~calculateOrientation
        ~forward
        ~geometries
        ~inverse
        ~refineLattice
        ~removeAllReflections

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
        ~sample
        ~UB
    """

    name = "hkl_soleil"
    version = libhkl.VERSION

    def __init__(
        self,
        geometry: str,
        *,
        engine: str = "hkl",
        mode: str = "",
        **kwargs,
    ) -> None:
        self._engine = None
        self._gname_locked = False  # Can't change after setting once.
        self._sample = None

        super().__init__(geometry, **kwargs)

        # note: must keep the '_engine_list' object as class attribute or
        # random core dumps, usually when accessing 'engine.name_get()'.
        self._detector = libhkl.Detector.factory_new(
            libhkl.DetectorType(LIBHKL_DETECTOR_TYPE)
        )
        self._factory = libhkl.factories()[geometry]
        self._engine_list = self._factory.create_new_engine_list()  # note!
        self._engine = self._engine_list.engine_get_by_name(engine)
        self._geometry = self._factory.create_new_geometry()

    def __repr__(self) -> str:
        args = [
            f"{s}={getattr(self, s)!r}"
            for s in "name version geometry engine mode".split()
        ]
        return f"{self.__class__.__name__}({', '.join(args)})"

    def addReflection(self, reflection: Reflection) -> None:
        """Add coordinates of a diffraction condition (a reflection)."""
        if not isinstance(reflection, Reflection):
            raise TypeError(f"Must supply Reflection object, received {reflection!r}")

        logger.debug("reflection: %r", reflection)
        pseudos = list(reflection.pseudos.values())
        reals = list(reflection.reals.values())
        wavelength = reflection.wavelength
        self._geometry.axis_values_set(reals, LIBHKL_USER_UNITS)
        self._geometry.wavelength_set(wavelength, LIBHKL_USER_UNITS)
        self.sample.add_reflection(self._geometry, self._detector, *pseudos)

    @property
    def axes_c(self) -> list[str]:
        """
        HKL real axis names.

        Held constant during 'forward()' computation.
        """
        # Do NOT sort.
        return [axis for axis in self.axes_r if axis not in self.axes_w]

    @property
    def axes_r(self) -> list[str]:
        """HKL real axis names (read-only)."""
        return self._engine.axis_names_get(AXES_READ)  # Do NOT sort.

    @property
    def axes_w(self) -> list[str]:
        """
        HKL real axis names.

                Updated by 'forward()' computation.
        """
        return self._engine.axis_names_get(AXES_WRITTEN)  # Do NOT sort.

    def calculateOrientation(
        self,
        r1: Reflection,
        r2: Reflection,
    ) -> list[list[float]]:
        """Calculate the UB (orientation) matrix from two reflections."""
        if self.sample is None:
            return
        # Remove all reflections first
        self.removeAllReflections()
        self.addReflection(r1)
        self.addReflection(r2)
        self.sample.compute_UB_busing_levy(*self.sample.reflections_get())
        logger.debug("%r reflections", len(self.sample.reflections_get()))
        return self.UB

    @property
    def engine(self) -> libhkl.Engine:
        """Selected computational engine for this geometry."""
        return self._engine.name_get()

    @property
    def engines(self) -> list[str]:
        """List of the computational engines available in this geometry."""
        return [engine.name_get() for engine in self._engine_list.engines_get()]

    @property
    def extra_axis_names(self) -> list[str]:
        """
        Ordered list of any extra axis names (such as x, y, z).

        Depends on selected geometry, engine, and mode.
        """
        return self._engine.parameters_names_get()  # Do NOT sort.

    def forward(self, pseudos: dict) -> list[dict[str, float]]:
        """Compute list of solutions(reals) from pseudos (hkl -> [angles])."""
        logger.debug("(%r) forward(%r)", __name__, pseudos)
        values = list(pseudos.values())
        geometry_list = self._engine.pseudo_axis_values_set(values, LIBHKL_USER_UNITS)
        solutions = []
        for glist_item in geometry_list.items():
            geo = glist_item.geometry_get()
            sol = dict(
                zip(
                    geo.axis_names_get(), 
                    _roundoff(geo.axis_values_get(LIBHKL_USER_UNITS)),
                )
            )
            solutions.append(sol)
        return solutions

    @classmethod
    def geometries(cls) -> list[str]:
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

    def inverse(self, reals: dict[str, float]) -> dict[str, float]:
        """Compute tuple of pseudos from reals (angles -> hkl)."""
        logger.debug("{__name__=} inverse(reals=%r)", reals)
        if list(reals) != self.real_axis_names:
            raise ValueError(
                f"Wrong dictionary keys received: {list(reals)!r}"
                f" Expected: {self.real_axis_names!r}"
            )
        if False in [isinstance(v, (float, int)) for v in reals.values()]:
            # fmt: off
            raise TypeError(
                "All dictionary must be numbers."
                f"  Received: {reals!r}"
            )
            # fmt: on

        # print(f"{reals=!r}")
        # print(f"{self._engine.pseudo_axis_values_get(LIBHKL_USER_UNITS)=!r}")
        reals = list(reals.values())
        # print(f"{reals=!r}")
        self._geometry.axis_values_set(reals, LIBHKL_USER_UNITS)
        # print(f"{self._geometry.axis_values_get(LIBHKL_USER_UNITS)=!r}")

        self._engine_list.get()  # reals -> pseudos  (Odd name for this call!)

        # print(f"{self._geometry.axis_values_get(LIBHKL_USER_UNITS)=!r}")
        pdict = dict(
            zip(
                self._engine.pseudo_axis_names_get(),
                _roundoff(self._engine.pseudo_axis_values_get(LIBHKL_USER_UNITS)),
            )
        )
        return pdict
    
    @property
    def lattice(self) -> libhkl.Lattice:
        """
        Crystal lattice parameters.  (Not used by this |solver|.)
        """
        return self.sample.lattice_get()

    @lattice.setter
    def lattice(self, value):
        if not isinstance(value, Lattice):
            raise TypeError(f"Must supply Lattice object, received {value!r}")

        self.sample.lattice_set(
            libhkl.Lattice.new(
                value.a,
                value.b,
                value.c,
                math.radians(value.alpha),
                math.radians(value.beta),
                math.radians(value.gamma),
            )
        )
        logger.debug(
            "sample lattice: %r",
            self.sample.lattice_get().get(LIBHKL_USER_UNITS),
        )

    @property
    def mode(self) -> str:
        """Name of the current geometry operating mode."""
        return self._engine.current_mode_get()

    @mode.setter
    def mode(self, value: str):
        check_value_in_list("Mode", value, self.modes, blank_ok=True)
        if value == "":
            return  # keep current mode
        self._engine.current_mode_set(value)

    @property
    def modes(self) -> list[str]:
        """List of the geometry operating modes."""
        if self._engine is None:
            return []
        return self._engine.modes_names_get()

    @property
    def pseudo_axis_names(self) -> list[str]:
        """Ordered list of the pseudo axis names (such as h, k, l)."""
        return self._engine.pseudo_axis_names_get()  # Do NOT sort.

    @property
    def real_axis_names(self) -> list[str]:
        """Ordered list of the real axis names (such as th, tth)."""
        return self._geometry.axis_names_get()  # Do NOT sort.

    def refineLattice(self, reflections: list[Reflection]) -> Lattice:
        """Refine the lattice parameters from a list of reflections."""
        self.removeAllReflections()
        for r in reflections:
            self.addReflection(r)
        # TODO:
        # self.sample.affine(*self.sample.reflections_get())
        # get the refined lattice
        # return Lattice()

    def removeAllReflections(self) -> None:
        """Remove all reflections."""
        refs = self.sample.reflections_get()
        for ref in refs:
            self.sample.del_reflection(ref)

    @property
    def sample(self) -> libhkl.Sample:
        """
        Crystalline sample.  libhkl's sample object.
        """
        return self._sample

    @sample.setter
    def sample(self, value: Sample):
        if not isinstance(value, Sample):
            raise TypeError(f"Must supply Sample object, received {value!r}")

        # Just drop the old sample and make a new one.
        # Python knows its correct name.
        # Doesn't matter what name is used by libhkl. Use a unique name.
        sample = libhkl.Sample.new(unique_name())  # new sample each time
        self._sample = sample
        self._engine_list.init(self._geometry, self._detector, sample)
        logger.debug(
            "sample name=%r, libhkl name=%r",
            value.name,
            sample.name_get(),
        )

        self.lattice = value.lattice

        logger.debug("%r ordering reflections: %r", value.reflections.order)
        for name in value.reflections.order:
            self.addReflection(value.reflections[name])
        # print(f"{sample.reflections_get()=!r}")

    @property
    def UB(self) -> list[list[float]]:
        """Orientation matrix (3x3)."""
        if self.sample is None:
            return IDENTITY_MATRIX_3X3
        matrix = self.sample.UB_get()
        return [
           _roundoff([matrix.get(i, j) for j in range(3)])
            for i in range(3)
        ]
