"""
Operate the diffractometer using a |solver| library and geometry.

Intermediate layer between DiffractometerBase Device and backend |solver|
library.

.. autosummary::

    ~Core
"""

import datetime
import logging
from collections.abc import Iterable
from typing import List
from typing import Optional
from typing import Union

from .backends.base import SolverBase
from .blocks.configure import Configuration
from .blocks.constraints import RealAxisConstraints
from .blocks.lattice import Lattice
from .blocks.reflection import Reflection
from .blocks.sample import Sample
from .misc import AnyAxesType
from .misc import AxesDict
from .misc import CoreError
from .misc import axes_to_dict
from .misc import solver_factory
from .misc import unique_name

__all__ = ["Core"]

Number = Union[int, float]
logger = logging.getLogger(__name__)
DEFAULT_SAMPLE_NAME = "sample"


class Core:
    """
    Core operations of a diffractometer, coordinating with sample & |solver|.

    .. rubric:: Parameters

    diffractometer (DiffractometerBase):
        The diffractometer parent.
    default_sample (bool):
        If 'True' (default), create a 'sample' with 1 angstrom cubic lattice.

    .. rubric:: Python Methods

    .. autosummary::

        ~_asdict
        ~_fromdict
        ~_validate_pseudos
        ~add_reflection
        ~add_sample
        ~assign_axes
        ~calc_UB
        ~forward
        ~inverse
        ~local_pseudo_axes
        ~local_real_axes
        ~refine_lattice
        ~remove_sample
        ~reset_constraints
        ~reset_samples
        ~set_solver
        ~standardize_pseudos
        ~standardize_reals

    .. rubric:: Python Properties

    .. autosummary::

        ~geometry
        ~sample
        ~solver
    """

    from .blocks.sample import Sample

    def __init__(self, diffractometer, default_sample: bool = True) -> None:
        # axes names cross-reference
        # keys: diffractometer axis names
        # values: solver axis names
        self.axes_xref = {}
        self.diffractometer = diffractometer
        self._sample_name = None
        self._samples = {}
        self._solver = None
        self._solver_needs_update: bool = True
        self.constraints = None
        self.configuration = None

        if default_sample:
            # first sample is cubic, no reflections
            self.add_sample(DEFAULT_SAMPLE_NAME, 1)

    def _asdict(self):
        """Describe the diffractometer as a dictionary."""
        from .__init__ import __version__

        dfrct = self.diffractometer
        # 2025-02-26: Apparently not needed, not easy to setup either.
        #     Retain in comment, just in case...
        # if not hasattr(dfrct, "name") or not hasattr(dfrct, "_source"):
        #     return {}  # Ophyd Device not initialized yet.  Empty dict is OK.

        config = {
            "_header": {
                "datetime": str(datetime.datetime.now()),
                "hklpy2_version": __version__,
                "python_class": dfrct.__class__.__name__,
            },
            "name": self.diffractometer.name,
            "axes": {
                "pseudo_axes": self.diffractometer.pseudo_axis_names,
                "real_axes": self.diffractometer.real_axis_names,
                "axes_xref": self.axes_xref,
            },
            "sample_name": self.sample.name,
            "samples": {k: v._asdict() for k, v in self._samples.items()},
            "constraints": self.constraints._asdict(),
            "solver": self.solver._metadata,
        }
        config["_header"].update(self.diffractometer._source._asdict())

        if self.solver.name == "hkl_soleil":
            config["solver"]["engine"] = self.solver.engine_name
            config["axes"]["extra_axes"] = self.solver.extras

        return config

    def _fromdict(self, config):
        """Redefine diffractometer from a (configuration) dictionary."""
        for key, sample in config["samples"].items():
            sample_object = self.add_sample(key, 1, replace=True)
            sample_object._fromdict(sample, core=self)
        sname = config.get("sample_name")
        if sname is not None:
            self.sample = sname

        for key, constraint in config["constraints"].items():
            if (
                constraint["class"] == "LimitsConstraint"
                and constraint["label"] in config["axes"]["real_axes"]
            ):
                # By convention, the 'key' here is the axis name when config was written.
                axis_canonical = config["axes"]["axes_xref"][key]
                axis_local = self.axes_xref_reversed[axis_canonical]
                constraint["label"] = axis_local
        self.constraints._fromdict(config["constraints"], core=self)

    def _validate_pseudos(self, pseudos) -> bool:
        """Validate that the supplied pseudos are acceptable."""
        if not isinstance(pseudos, Iterable):
            raise TypeError(
                "Pseudos must be tuple, list, or dict."
                # Always show the input.
                f"  Received {pseudos!r}"
            )
        if not isinstance(pseudos, (dict, list, set, tuple)):
            raise TypeError(f"Unexpected data type: {pseudos}")

        expected_names = self.local_pseudo_axes
        if len(pseudos) != len(expected_names):
            raise ValueError(
                f"Expected {len(expected_names)} pseudos,"
                # Always show the input.
                f" received {pseudos}"
            )

        original = pseudos  # Keep the original for reporting.
        if hasattr(pseudos, "_asdict"):
            pseudos = pseudos._asdict()
        if isinstance(pseudos, (list, set, tuple)):
            # Expect values are provided in canonical order.
            pseudos = {
                axis: value
                # rewrite as dictionary
                for axis, value in zip(expected_names, pseudos)
            }
        for axis in expected_names:
            if axis not in pseudos:
                raise ValueError(f"Wrong axis names: received {original}")
            if not isinstance(pseudos[axis], (float, int)):
                raise TypeError(f"Must be number, received {original}")

        return True

    def add_reflection(
        self,
        pseudos: AnyAxesType,
        reals: Union[AnyAxesType, None] = None,
        wavelength=None,
        name=None,
        replace: bool = False,
    ) -> Reflection:
        """
        Add a new reflection.

        .. rubric:: Parameters

        * ``pseudos`` (various): pseudo-space axes and values.
        * ``reals`` (various): dictionary of real-space axes and values.
        * ``wavelength`` (float): Wavelength of incident radiation.
        * ``name`` (str): Reference name for this reflection.
          If ``None``, a random name will be assigned.
        * ``replace`` (bool): If ``True``, replace existing reflection of
          this name.  (default: ``False``)
        """
        from .blocks.reflection import Reflection

        self._validate_pseudos(pseudos)

        logger.debug(
            "name=%r, geometry=%r, wavelength=%r",
            name,
            self.solver.geometry,
            wavelength,
        )

        pnames = self.local_pseudo_axes
        rnames = self.local_real_axes
        pdict = self.standardize_pseudos(pseudos)
        rdict = self.standardize_reals(reals)
        logger.debug(
            "pdict=%r, rdict=%r, pnames=%r, rnames=%r",
            pdict,
            rdict,
            pnames,
            rnames,
        )
        refl = Reflection(
            name or unique_name(),
            pdict,
            rdict,
            wavelength,
            self.solver.geometry,
            pnames,
            rnames,
        )
        self.sample.reflections.add(refl, replace=replace)
        return refl

    def add_sample(
        self,
        name: str,
        a: float,
        b: float = None,
        c: float = None,
        alpha: float = 90.0,  # degrees
        beta: float = None,  # degrees
        gamma: float = None,  # degrees
        digits: int = 4,
        replace: bool = False,
    ) -> Sample:
        """Add a new sample."""
        if name in self.samples:
            if not replace:
                raise CoreError(f"Sample {name=!r} already defined.")
        lattice = Lattice(a, b, c, alpha, beta, gamma, digits)
        self._samples[name] = Sample(self, name, lattice)
        self.sample = name
        self._solver_needs_update = True  # 58  test_diffract line 410: 2 pi a
        if self.solver is not None:
            self.solver.sample = self.sample
        return self.sample

    def assign_axes(self, pseudos: list[str], reals: list[str]) -> None:
        """
        Designate attributes for use by the PseudoPositioner class.

        Result is re-definition of 'self.axes_xref'.
        """
        pseudos = pseudos or []
        reals = reals or []

        def itemize(label, select, full):
            keys = [name for name, _obj in full]
            for attr in select:
                if attr not in keys:
                    raise KeyError(f"Unknown {label}={attr!r}.  Known: {keys!r}")
            return keys

        def rebuild_axes_xref(dnames, snames):
            for dname, sname in zip(dnames, snames):
                self.axes_xref[dname] = sname
                both_p_r.remove(dname)

        # check for duplicates
        if len(set(pseudos + reals)) != len(pseudos + reals):
            raise ValueError("Axis name cannot be in more than list.")

        if self.solver is None:
            return  # such as initialization

        dfrct = self.diffractometer
        all_pseudos = itemize("pseudo", pseudos, dfrct._get_pseudo_positioners())
        all_reals = itemize("real", reals, dfrct._get_real_positioners())
        both_p_r = all_pseudos + all_reals

        self.axes_xref = {}
        rebuild_axes_xref(pseudos, self.solver.pseudo_axis_names)
        rebuild_axes_xref(reals, self.solver.real_axis_names)
        self.reset_constraints()
        logger.debug("axes_xref=%r", self.axes_xref)
        self.configuration = Configuration(self.diffractometer)

    def _axes_names_s2d(self, axis_dict: dict[str, float]) -> dict[str, float]:
        """Convert keys of axis dictionary from solver to diffractometer."""
        reverse = self.axes_xref_reversed
        return {reverse[k]: v for k, v in axis_dict.items()}

    def _axes_names_d2s(self, axis_dict: dict[str, float]) -> dict[str, float]:
        """Convert keys of axis dictionary from diffractometer to solver."""
        return {self.axes_xref[k]: v for k, v in axis_dict.items()}

    @property
    def axes_xref_reversed(self):
        """Map axis names from solver to diffractometer."""
        if len(self.axes_xref) == 0:
            if self.solver is not None:
                names = self.solver.pseudo_axis_names + self.solver.real_axis_names
                if len(names) == 0:
                    return {}
            raise CoreError("Did you forget to call `assign_axes()`?")
        return {v: k for k, v in self.axes_xref.items()}

    def calc_UB(
        self, r1: Union[Reflection, str], r2: Union[Reflection, str]
    ) -> List[List[Number]]:
        """
        Calculate and return the UB (orientation) matrix with two reflections.

        The method of Busing & Levy, Acta Cryst 22 (1967) 457.
        """

        def _get(r):
            """Given a reference, get the Reflection object."""
            if isinstance(r, Reflection):
                return r
            reflection = self.sample.reflections.get(r)
            if reflection is None:
                raise KeyError(
                    f"{reflection!r} unknown."
                    f"  Knowns: {list(self.sample.reflections)!r}"
                )
            return reflection

        two_reflections = [_get(r1), _get(r2)]
        self.sample.reflections.set_orientation_reflections(two_reflections)
        ub = self.solver.calculate_UB(*two_reflections)
        self.sample.U = self.solver.U
        self.sample.UB = ub
        self._solver_needs_update = False
        return ub

    def forward(self, pseudos: AnyAxesType, wavelength: float = None) -> list:
        """Compute [{names:reals}] from {names: pseudos} (hkl -> angles)."""
        logger.debug(
            "(%s) forward(): pseudos=%r",
            self.__class__.__name__,
            pseudos,
        )

        pdict = self.standardize_pseudos(pseudos)
        reals = self.diffractometer.real_position._asdict()  # Original values.

        self.update_solver(wavelength=wavelength)

        # Filter just the solutions that fit the constraints.
        results = self.solver.forward(self._axes_names_d2s(pdict))
        solutions = []
        for solution in results:
            reals.update(self._axes_names_s2d(solution))  # Update with new values.
            if self.constraints.valid(**reals):
                solutions.append(self.diffractometer.RealPosition(**reals))

        return solutions

    def inverse(
        self, reals: Union[AnyAxesType, None], wavelength: float = None
    ) -> AxesDict:
        """Compute (pseudos) from {names: reals} (angles -> hkl)."""
        logger.debug(
            "(%s) inverse(): reals=%r",
            self.__class__.__name__,
            reals,
        )
        pseudos: AxesDict = {
            axis[0]: 0
            # Original values.
            for axis in self.diffractometer._get_pseudo_positioners()
        }
        if self.solver is None:
            # Called from the constructor before solver is defined.
            return pseudos  # current values of pseudos

        # Just the reals expected by the solver.
        # Dictionary in order expected by the solver.
        reals: AxesDict = self.standardize_reals(reals)

        self.update_solver(wavelength=wavelength)

        # transform: reals -> pseudos
        spdict: AxesDict = self.solver.inverse(self._axes_names_d2s(reals))

        pseudos.update(self._axes_names_s2d(spdict))  # Update with new values.
        return pseudos

    @property
    def local_pseudo_axes(self) -> list:
        """
        List of the diffractometer pseudo axes expected by the solver.

        This becomes useful when additional pseudo axes are named
        as ophyd Components in the diffractometer.
        """
        if self.solver is None:
            return []
        return [
            self.axes_xref_reversed[k]
            #
            for k in self.solver.pseudo_axis_names
        ]

    @property
    def local_real_axes(self) -> list:
        """
        List of the diffractometer real axes expected by the solver.

        This becomes useful when additional real axes are named
        as ophyd Components in the diffractometer.
        """
        if self.solver is None:
            return []
        return [
            self.axes_xref_reversed[k]
            #
            for k in self.solver.real_axis_names
        ]

    def refine_lattice(self, reflections: list = None) -> Lattice:
        """
        Return the sample lattice computed from 3 or more reflections.

        Do not change the sample lattice.  Let the user decide that.
        """
        if reflections is None:
            reflections = list(self.sample.reflections.values())
        logger.debug(
            "Refining lattice using reflections %r",
            [r.name for r in reflections],
        )
        lattice = self.solver.refineLattice(reflections)
        return lattice

    def remove_sample(self, name):
        """Remove the named sample.  No error if name is not known."""
        if name not in self.samples:
            raise KeyError(f"{name!r} not in sample list:{list(self.samples)}.")
        if len(self.samples) == 1:
            raise CoreError("Cannot remove last sample.")

        self._samples.pop(name)
        self._sample_name = list(self.samples)[0]

    def reset_constraints(self):
        """Restore diffractometer constraints to default settings."""
        self.constraints = RealAxisConstraints(self.diffractometer.real_axis_names)

    def reset_samples(self):
        """Restore diffractometer samples to default settings."""
        self._samples = {}  # Remove all the samples.
        # Create the default sample.
        self.add_sample(DEFAULT_SAMPLE_NAME, 1)

    def set_solver(
        self,
        name: str,
        geometry: str,
        **kwargs: dict,
    ) -> SolverBase:
        """
        Create an instance of the backend |solver| library and geometry.

        .. rubric:: Parameters

        * ``solver`` (str): Name of the |solver| library.
        * ``geometry`` (str): Name of the |solver| geometry.
        * ``kwargs`` (dict): Any keyword arguments needed by the |solver|.
        """
        logger.debug(
            "(%s) solver=%r, geometry=%r, kwargs=%r",
            self.__class__.__name__,
            name,
            geometry,
            kwargs,
        )
        self._solver = solver_factory(name, geometry, **kwargs)
        self.update_solver()
        self._solver_needs_update = True
        return self._solver

    def standardize_pseudos(self, pseudos: AnyAxesType) -> AxesDict:
        """
        Convert user-supplied pseudos into dictionary in solver's order.

        User could provide pseudos in several forms:

        * dict: {"h": 0, "k": 1, "l": -1}
        * namedtuple: (h=0.0, k=1.0, l=-1.0)
        * ordered list: [0, 1, -1]  (for h, k, l)
        * ordered tuple: (0, 1, -1)  (for h, k, l)
        """
        return axes_to_dict(pseudos, self.local_pseudo_axes)

    def standardize_reals(self, reals: Union[AnyAxesType, None]) -> AxesDict:
        """
        Convert user-supplied reals into dictionary in solver's order.

        User could provide reals in several forms:

        * None: current positions
        * dict: {"omega": 120, "chi": 35.3, "phi": 45, "tth": -120}
        * namedtuple: (omega=120, chi=35.3, phi=45, tth=-120)
        * ordered list: [120, 35.3, 45, -120]  (for omega, chi, phi, tth)
        * ordered tuple: (120, 35.3, 45, -120)  (for omega, chi, phi, tth)
        """

        if reals is None:  # write ordered dict
            reals = {
                k: getattr(self.diffractometer, k).position
                # Get from current diffractometer axis positions
                for k in self.local_real_axes
            }

        return axes_to_dict(reals, self.local_real_axes)

    def update_solver(self, wavelength: Optional[float] = None) -> None:
        """Update solver data if needed."""
        if self._solver_needs_update or wavelength is not None:
            self.solver.sample = self.sample  # lattice & reflections
            self.solver.wavelength = wavelength or self.diffractometer.wavelength.get()
            # print(f"DEBUG update_solver(): {self.sample.UB=}")
            try:
                self.solver.U = self.sample.U
                self.solver.UB = self.sample.UB
            except AttributeError:
                pass  # Some solvers have no setter for U & UB
            self._solver_needs_update = False

    # ---- get/set properties

    @property
    def geometry(self) -> str:
        """Backend |solver| geometry name."""
        return self.solver.geometry

    @property
    def sample(self) -> Sample:
        """Current Sample (Python object)."""
        return self.samples[self._sample_name]

    @sample.setter
    def sample(self, value: str) -> None:
        self._sample_name = value
        if self.solver is not None:
            try:
                self.solver.U = self.sample.U
                self.solver.UB = self.sample.UB
            except AttributeError:
                pass  # property is not settable

    @property
    def samples(self) -> dict:
        """Sample dictionary."""
        return self._samples

    @property
    def solver(self) -> SolverBase:
        """Backend |solver| object."""
        return self._solver
