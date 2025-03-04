r"""
"hkl_soleil" solver, provides **Hkl**, Synchrotron Soleil.

Example::

    >>> import hklpy2
    >>> SolverClass = hklpy2.get_solver("hkl_soleil")
    >>> libhkl_solver = SolverClass(geometry="E4CV")
    >>> solver
    HklSolver(name='hkl_soleil', version='v5.0.0.3434', geometry='E4CV', engine='hkl', mode='bissector')

:home: https://people.debian.org/~picca/hkl/hkl.html
:source: https://repo.or.cz/hkl.git
:conda-forge: https://anaconda.org/conda-forge

..  caution:: The ``hkl_soleil`` |solver| is not available
    for Windows or Mac OS.  The underlying |libhkl| support
    library is only provided
    for Linux 64-bit OS at this time.

.. note:: To hold an axis or extra parameter constant (current or specified value):
    choose the mode and set the parameter before the forward() transformation.

.. note:: To scan using ``psi`` and ``hkl2``, see
    :doc:`../../examples/hkl_soleil-e6c-psi`.

.. autosummary::

    ~HklSolver
"""

# Notes:
#
# - 'fit'
#     While this parameter is used by *libhkl* to adjust lattice parameters when
#     refining from more than 2 reflections, it is not used in the calculation of
#     rotation angles from reciprocal-space coordinates.

import logging
import math
import platform

from pyRestTable import Table

from .. import SolverBase
from .. import SolverError
from .. import check_value_in_list
from ..blocks.lattice import Lattice
from ..blocks.reflection import Reflection
from ..blocks.sample import Sample
from ..misc import IDENTITY_MATRIX_3X3
from ..misc import roundoff
from ..misc import unique_name

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
ROUNDOFF_DIGITS = 12


def roundoff_list(values, digits=ROUNDOFF_DIGITS):
    """Prevent underflows and '-0' for all numbers in a list."""
    return [roundoff(v, digits) for v in values]


def hkl_euler_matrix(euler_x, euler_y, euler_z):
    """Convert into matrix form."""
    return libhkl.Matrix.new_euler(euler_x, euler_y, euler_z)


def to_hkl(arr):
    """Convert a numpy ndarray to an hkl ``Matrix``

    Parameters
    ----------
    arr : ndarray

    Returns
    -------
    Hkl.Matrix
    """
    import numpy as np

    if isinstance(arr, libhkl.Matrix):
        return arr

    arr = np.array(arr)

    hklm = hkl_euler_matrix(0, 0, 0)
    hklm.init(*arr.flatten())
    return hklm


def to_numpy(mat):
    """Convert an hkl ``Matrix`` to a numpy ndarray

    Parameters
    ----------
    mat : Hkl.Matrix

    Returns
    -------
    ndarray
    """
    import numpy as np

    if isinstance(mat, np.ndarray):
        return mat

    ret = np.zeros((3, 3))
    for i in range(3):
        for j in range(3):
            ret[i, j] = mat.get(i, j)

    return ret


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

    .. note:: The lists of ``pseudos`` and ``reals`` are the
       corresponding axes of the diffractometer, in the order expected by
       the |solver| geometry.  The diffractometer can use names that are
       different from the names expected by the engine here.  The
       :class:`~hklpys.ops.core` class will convert between the two
       sets of names.

    .. rubric:: Python Methods

    .. autosummary::

        ~addReflection
        ~calculate_UB
        ~forward
        ~geometries
        ~inverse
        ~refineLattice
        ~removeAllReflections
        ~summary

    .. rubric:: Python Properties

    .. autosummary::

        ~_summary
        ~axes_c
        ~axes_r
        ~axes_w
        ~engine
        ~engine_name
        ~engines
        ~extra_axis_names
        ~extras
        ~geometry
        ~lattice
        ~mode
        ~modes
        ~pseudo_axis_names
        ~real_axis_names
        ~sample
        ~UB
        ~wavelength
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
            for s in "name version geometry engine_name mode".split()
        ]
        return f"{self.__class__.__name__}({', '.join(args)})"

    def addReflection(self, reflection: Reflection) -> None:
        """Add coordinates of a diffraction condition (a reflection)."""
        if not isinstance(reflection, Reflection):
            raise TypeError(f"Must supply Reflection object, received {reflection!r}")

        logger.debug("reflection: %r", reflection)
        pseudos = list(reflection.pseudos.values())
        reals = list(reflection.reals.values())
        self.wavelength = reflection.wavelength
        self._geometry.axis_values_set(reals, LIBHKL_USER_UNITS)
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
        return self.engine.axis_names_get(AXES_READ)  # Do NOT sort.

    @property
    def axes_w(self) -> list[str]:
        """
        HKL real axis names.

                Updated by 'forward()' computation.
        """
        return self.engine.axis_names_get(AXES_WRITTEN)  # Do NOT sort.

    def calculate_UB(
        self,
        r1: Reflection,
        r2: Reflection,
    ) -> list[list[float]]:
        """
        Calculate the UB (orientation) matrix with two reflections.

        The method of Busing & Levy, Acta Cryst 22 (1967) 457.
        """
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
        return self._engine

    @property
    def engine_name(self) -> str:
        """Name of selected computational engine for this geometry."""
        return self.engine.name_get()

    @property
    def engines(self) -> list[str]:
        """List of the computational engines available in this geometry."""
        return [engine.name_get() for engine in self._engine_list.engines_get()]

    @property
    def extra_axis_names(self) -> list[str]:
        """
        Ordered list of any extra parameter names (such as x, y, z).

        Depends on selected geometry, engine, and mode.
        """
        return self.engine.parameters_names_get()  # Do NOT sort.

    @property
    def extras(self) -> dict:
        """
        Ordered dictionary of any extra parameters.

        Depends on selected geometry, engine, and mode.
        """
        return dict(
            zip(
                self.extra_axis_names,
                self.engine.parameters_values_get(LIBHKL_USER_UNITS),
            )
        )

    @extras.setter
    def extras(self, values: dict) -> None:
        known_names = self.extra_axis_names
        for k in values.keys():
            if k not in known_names:
                raise ValueError(
                    f"Unexpected dictionary key received: {k!r}"
                    f" Expected one of these: {known_names!r}"
                )
        for k, v in values.items():
            p = self.engine.parameter_get(k)
            p.value_set(v, LIBHKL_USER_UNITS)
            self.engine.parameter_set(k, p)

    def forward(self, pseudos: dict) -> list[dict[str, float]]:
        """Compute list of solutions(reals) from pseudos (hkl -> [angles])."""
        logger.debug("(%r) forward(%r)", __name__, pseudos)

        geometry_list = self.engine.pseudo_axis_values_set(
            list(pseudos.values()),
            LIBHKL_USER_UNITS,
        )

        solutions = []
        for glist_item in geometry_list.items():
            geo = glist_item.geometry_get()
            sol = dict(
                zip(
                    geo.axis_names_get(),
                    roundoff_list(geo.axis_values_get(LIBHKL_USER_UNITS)),
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

        reals = list(reals.values())
        self._geometry.axis_values_set(reals, LIBHKL_USER_UNITS)

        self._engine_list.get()  # reals -> pseudos  (Odd name for this call!)

        pdict = dict(
            zip(
                self.engine.pseudo_axis_names_get(),
                roundoff_list(self.engine.pseudo_axis_values_get(LIBHKL_USER_UNITS)),
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
        return self.engine.current_mode_get()

    @mode.setter
    def mode(self, value: str):
        check_value_in_list("Mode", value, self.modes, blank_ok=True)
        if value == "":
            return  # keep current mode
        self.engine.current_mode_set(value)

    @property
    def modes(self) -> list[str]:
        """List of the geometry operating modes."""
        if self.engine is None:
            return []
        return self.engine.modes_names_get()

    @property
    def pseudo_axis_names(self) -> list[str]:
        """Ordered list of the pseudo axis names (such as h, k, l)."""
        return self.engine.pseudo_axis_names_get()  # Do NOT sort.

    @property
    def real_axis_names(self) -> list[str]:
        """Ordered list of the real axis names (such as th, tth)."""
        return self._geometry.axis_names_get()  # Do NOT sort.

    def refineLattice(self, reflections: list[Reflection]) -> Lattice:
        """
        Refine the lattice parameters from a list of reflections.

        hkl_soleil uses a simplex method.
        """
        if len(reflections) < 3:
            raise ValueError("Must provide 3 or more reflections to refine lattice.")
        self.removeAllReflections()
        for r in reflections:
            self.addReflection(r)

        self.sample.affine()  # refine the lattice

        # get the refined lattice
        lattice = self.lattice.get(LIBHKL_USER_UNITS)
        return Lattice(
            lattice.a,
            lattice.b,
            lattice.c,
            lattice.alpha,
            lattice.beta,
            lattice.gamma,
        )

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
    def U(self) -> list[list[float]]:
        """
        Relative orientation of crystal on diffractometer.

        Rotation matrix,  (3x3).
        """
        if self.sample is None:
            return IDENTITY_MATRIX_3X3
        matrix = to_numpy(self.sample.U_get())
        return matrix.round(decimals=ROUNDOFF_DIGITS).tolist()

    @U.setter
    def U(self, value: list[list[float]]) -> None:
        if self.sample is not None:
            self.sample.U_set(to_hkl(value))

    @property
    def UB(self) -> list[list[float]]:
        """Orientation matrix (3x3)."""
        if self.sample is None:
            return IDENTITY_MATRIX_3X3
        matrix = to_numpy(self.sample.UB_get())
        return matrix.round(decimals=ROUNDOFF_DIGITS).tolist()

    @UB.setter
    def UB(self, value: list[list[float]]) -> None:
        if self.sample is not None:
            self.sample.UB_set(to_hkl(value))

    @property
    def wavelength(self) -> float:
        """Monochromatic wavelength."""
        return self._geometry.wavelength_get(LIBHKL_USER_UNITS)

    @wavelength.setter
    def wavelength(self, value: float) -> None:
        return self._geometry.wavelength_set(value, LIBHKL_USER_UNITS)

    @property
    def _summary(self):  # TODO: add to base class, TODO: needs tests
        """Return a summary of the geometry (engines, modes, axes)"""
        geometry_name = self.geometry
        description = {"name": geometry_name}
        factories = libhkl.factories()

        factory = factories[geometry_name]
        engine_list = factory.create_new_engine_list()

        engines = {engine.name_get(): engine for engine in engine_list.engines_get()}
        description["engines"] = {}
        for engine_name, engine in engines.items():
            eng_desc = {
                "pseudos": engine.pseudo_axis_names_get(),
                "reals": {},
                "modes": {},
            }
            description["engines"][engine_name] = eng_desc
            eng_desc["reals"] = engine.axis_names_get(AXES_READ)
            extras = []
            for mode_name in engine.modes_names_get():
                engine.current_mode_set(mode_name)
                eng_desc["modes"][mode_name] = {
                    "extras": engine.parameters_names_get(),
                    "reals": engine.axis_names_get(AXES_WRITTEN),
                }
                extras += eng_desc["modes"][mode_name]["extras"]
            eng_desc["extras"] = list(sorted(set(extras)))

        return description

    def summary(self) -> Table:  # TODO: add to base class, TODO: needs tests
        """Table of engines, modes, & axes for this geometry."""
        table = Table()
        table.labels = "engine pseudo(s) mode real(s) writable(s) extra(s)".split()
        for engine_name, engine in self._summary["engines"].items():
            row_start = [
                engine_name,
                ", ".join(engine["pseudos"]),
            ]
            for mode_name, mode in engine["modes"].items():
                row = row_start + [
                    mode_name,
                    ", ".join(engine["reals"]),
                    ", ".join(mode["reals"]),
                    ", ".join(mode["extras"]),
                ]
                table.addRow(row)

        return table
