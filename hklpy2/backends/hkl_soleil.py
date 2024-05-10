"""
Backend: Hkl (``"hkl_soleil"``)

Example::

    import hklpy2
    SolverClass = hklpy2.get_solver("hkl_soleil")
    libhkl_solver = SolverClass()

.. autosummary::

    ~HklSolver
"""


from .. import SolverError  # noqa: E402

try:
    import gi
except ModuleNotFoundError:
    raise SolverError("No gobject-introspection library.  Is libhkl installed?")

gi.require_version("Hkl", "5.0")

from gi.repository import GLib  # noqa: E402, F401, W0611
from gi.repository import Hkl as libhkl  # noqa: E402

from .. import SolverBase  # noqa: E402


class HklSolver(SolverBase):
    """
    ``"hkl_soleil"`` (Linux x86_64 only) |libhkl|.

    |solver| with support for many common diffractometer geoemtries.
    Wraps the |libhkl| library from Frédéric-Emmanuel PICCA (Soleil).

    .. autosummary::

        ~addReflection
        ~addSample
        ~calculateOrientation
        ~forward
        ~geometries
        ~geometry
        ~inverse
        ~lattice
        ~modes
        ~pseudo_axis_names
        ~real_axis_names
        ~refineLattice
    """

    __name__ = "hkl_soleil"
    __version__ = libhkl.VERSION

    def __init__(self) -> None:
        super().__init__()

        self.detector = libhkl.Detector.factory_new(libhkl.DetectorType(0))
        self._factory = None
        self._geometry = None
        self.user_units = libhkl.UnitEnum.USER
        self._pseudo_axis_names = []
        self._real_axis_names = []

    def addReflection(self, pseudos, reals, wavelength):  # TODO
        """Add information about a reflection."""

    def addSample(self, sample):  # TODO
        """Add a sample."""

    def calculateOrientation(self, r1, r2):  # TODO
        """Calculate the UB (orientation) matrix from two reflections."""

    def forward(self):
        """Compute list of solutions(reals) from pseudos (hkl -> [angles])."""
        return [{}]

    @property
    def geometries(self):
        """
        Ordered list of the geometry names.

        .. sidebar:: compare with E4CV

            TODO: confirm with the |libhkl| docs

            .. seealso::

                * `E4CV <https://blueskyproject.io/hklpy/geometry_tables.html#geometry-e4cv>`_
                * `Hkl <https://people.debian.org/~picca/hkl/hkl.html>`_

        For |libhkl|, each geometry may have zero or more computational
        *engines*. Each engine has its own set of pseudos and reals.  Some of
        the engines have additional (optional) axes.

        So the geometry *names* include both the geometry and its computational
        engine, such as `"E4CV, hkl"`.

        """
        geometries = []
        for fname, factory in libhkl.factories().items():
            # Underlying library raises error for the merged call:
            #   factory.create_new_engine_list().engines_get()
            # MUST do this in two parts here (and elsewhere).
            engines = factory.create_new_engine_list()
            for engine in engines.engines_get():
                # "geometry, engine"
                geometries.append(f"{fname}, {engine.name_get()}")
        return sorted(set(geometries))

    @property
    def geometry(self):
        """
        Diffractometer geometry and engine, such as `"E4CV, hkl"`.

        To select (set) which combination of geometry and computational
        engine, specify both such as::

            solver.geometry = "E4CV, hkl"
        """
        return self._geometry

    @geometry.setter
    def geometry(self, value):
        if not isinstance(value, (type(None), str)):
            raise TypeError(f"Must supply str, received {value!r}")
        if value not in self.geometries:
            raise KeyError(f"Geometry {value} unknown.")

        self._geometry = value

        gname, engine = [s.strip() for s in value.split(",")]
        self._factory = libhkl.factories()[gname]
        engines = self._factory.create_new_engine_list()
        engine = engines.engine_get_by_name(engine)

        g = self._factory.create_new_geometry()
        self._real_axis_names = g.axis_names_get()
        self._pseudo_axis_names = engine.pseudo_axis_names_get()

    def inverse(self, reals: dict):
        """Compute tuple of pseudos from reals (angles -> hkl)."""
        return tuple()  # TODO

    @property
    def modes(self):
        """List of the geometry operating modes."""
        return []  # TODO

    @property
    def pseudo_axis_names(self):
        """Ordered list of the pseudo axis names (such as h, k, l)."""
        return self._pseudo_axis_names

    @property
    def real_axis_names(self):
        """Ordered list of the real axis names (such as th, tth)."""
        return self._real_axis_names

    def refineLattice(self, reflections):
        """Refine the lattice parameters from a list of reflections."""
        pass  # TODO

    def setLattice(self, lattice):
        """Define the sample's lattice parameters."""
        pass  # TODO
