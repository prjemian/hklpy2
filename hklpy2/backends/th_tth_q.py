"""
Backend: th_tth (``"th_tth"``)

Transformations between :math:`\\theta,2\\theta` and :math:`Q`.

Example::

    import hklpy2
    SolverClass = hklpy2.get_solver("th_tth")
    solver = SolverClass()

.. autosummary::

    ~ThTthSolver
"""

import math

from .. import Reflection
from .. import SolverError
from .. import __version__
from .base import SolverBase

TH_TTH_Q_GEOMETRY = "TH TTH Q"


class ThTthSolver(SolverBase):
    """
    ``"th_tth"`` (any OS) :math:`\\theta,2\\theta` and :math:`Q`.

    ============== =================
    transformation equation
    ============== =================
    ``forward()``  :math:`\\theta = \\sin^{-1}(q\\lambda / 4\\pi)`
    ``inverse()``  :math:`q = (4\\pi / \\lambda) \\sin(\\theta)`
    ============== =================

    Wavelength is specified either directly (``solver.wavelength = 1.0``) or
    by adding at least one :index:`reflection` (see :class:`Reflection`).  All
    reflections must have the same :index:`wavelength`.

    No orientation matrix is used in this geometry.

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

    __name__ = "th_tth"
    __version__ = __version__

    def __init__(self) -> None:
        super().__init__()
        self._geometry = None
        self._reflections = []
        self._wavelength = None

    def addReflection(self, value: Reflection):
        if not isinstance(value, Reflection):
            raise TypeError(f"Must supply Reflection object, received {value!r}")
        self._reflections.append(value)

        # validate: all reflections must have same wavelength
        wavelengths = [r.wavelength for r in self._reflections]
        if min(wavelengths) != max(wavelengths):
            self._reflections.pop(-1)
            raise SolverError(
                "All reflections must have same wavelength.  "
                f"Received: {wavelengths!r}"
            )
        self.wavelength = wavelengths[0]

    def addSample(self, sample):
        pass  # ignored

    def calculateOrientation(self, r1, r2):
        return []

    def forward(self, pseudos):
        """Transform pseudos to list of reals."""
        if not isinstance(pseudos, dict):
            raise TypeError(f"Must supply dict, received {pseudos!r}")

        solutions = []
        if self.geometry == TH_TTH_Q_GEOMETRY:
            q = pseudos.get("q")
            if q is None:
                raise SolverError(f"'q' not defined. Received {pseudos!r}.")
            if self.wavelength is None:
                raise SolverError(
                    "Wavelength is not set. Set wavelength or add reflection."
                )
            if self.mode == "bisector":
                th = math.degrees(math.asin(q * self.wavelength / 4 / math.pi))
                solutions.append({"th": th, "tth": 2 * th})

        return solutions

    @property
    def geometries(self):
        return [TH_TTH_Q_GEOMETRY]  # only one geometry

    @property
    def geometry(self):
        """Diffractometer geometry."""
        return self._geometry

    @geometry.setter
    def geometry(self, value):
        if not isinstance(value, (type(None), str)):
            raise TypeError(f"Must supply str, received {value!r}")
        if value not in self.geometries:
            raise KeyError(f"Geometry {value} unknown.")
        self._geometry = value

    def inverse(self, reals: dict):
        """Transform reals to pseudos."""
        if not isinstance(reals, dict):
            raise TypeError(f"Must supply dict, received {reals!r}")

        pseudos = {}
        if self.geometry == TH_TTH_Q_GEOMETRY:
            tth = reals.get("tth")
            if tth is None:
                raise SolverError(f"'tth' not defined. Received {reals!r}.")
            if self.wavelength is None:
                raise SolverError(
                    "Wavelength is not set. Set wavelength or add reflection."
                )
            if self.mode == "bisector":
                q = (4 * math.pi) / self.wavelength
                q *= math.sin(math.radians(tth / 2))
                pseudos["q"] = q
        return pseudos

    @property
    def modes(self):
        if self.geometry == TH_TTH_Q_GEOMETRY:
            return ["bisector"]

    @property
    def pseudo_axis_names(self):
        axes = {TH_TTH_Q_GEOMETRY: ["q"]}
        return axes.get(self.geometry, [])

    @property
    def real_axis_names(self):
        axes = {TH_TTH_Q_GEOMETRY: "th tth".split()}
        return axes.get(self.geometry, [])

    def refineLattice(self, reflections): ...  # ignored

    def setLattice(self, lattice): ...  # ignored

    @property
    def wavelength(self):
        """Diffractometer wavelength, for forward() and inverse()."""
        return self._wavelength

    @wavelength.setter
    def wavelength(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError(f"Must supply number, received {value!r}")
        if value <= 0:
            raise ValueError(f"Must supply positive number, received {value!r}")
        self._wavelength = value
