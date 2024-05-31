"""
Operate the diffractometer using a |solver| library and geometry.

Intermediate layer between DiffractometerBase Device and backend |solver|
library.

.. autosummary::

    ~Operations
"""

import logging

from . import Hklpy2Error
from . import SolverBase
from .operations.lattice import Lattice
from .operations.misc import solver_factory
from .operations.misc import unique_name
from .operations.reflection import Reflection
from .operations.sample import Sample

__all__ = "Operations OperationsError".split()
logger = logging.getLogger(__name__)


class OperationsError(Hklpy2Error):
    """Custom exceptions from :class:`~Operations`."""


class Operations:
    """
    Operate the diffractometer using a |solver|.

    .. rubric:: Parameters

    * ``solver`` (str): Name of the backend |solver| library.
    * ``geometry`` (str): Name of the backend |solver| geometry.

    .. rubric:: Python Methods

    .. autosummary::

        ~add_reflection
        ~add_sample
        ~assign_axes
        ~auto_assign_axes
        ~calcUB
        ~forward
        ~inverse
        ~remove_sample
        ~set_solver
        ~standardize_pseudos
        ~standardize_reals

    .. rubric:: Python Properties

    .. autosummary::

        ~geometry
        ~sample
        ~solver
    """

    from .operations.sample import Sample

    def __init__(self, diffractometer, default_sample: bool = True) -> None:
        # axes names cross-reference
        # keys: diffractometer axis names
        # values: solver axis names
        self.axes_xref = {}
        self.diffractometer = diffractometer
        self._sample_name = None
        self._samples = {}
        self._solver = None

        if default_sample:
            # first sample is cubic, no reflections
            self.add_sample("cubic", 1)

    def add_reflection(
        self,
        pseudos,
        reals=None,
        wavelength=None,
        name=None,
    ) -> Reflection:
        """
        Add a new reflection.

        .. rubric:: Parameters

        * ``pseudos`` (various): pseudo-space axes and values.
        * ``reals`` (various): dictionary of real-space axes and values.
        * ``wavelength`` (float): Wavelength of incident radiation.
        * ``name`` (str): Reference name for this reflection.
          If ``None``, a random name will be assigned.
        """
        from .operations.reflection import Reflection

        reverse = self.axes_xref_reversed
        pnames = [reverse[k] for k in self.solver.pseudo_axis_names]
        rnames = [reverse[k] for k in self.solver.real_axis_names]
        pdict = self.standardize_pseudos(pseudos, pnames)
        rdict = self.standardize_reals(reals, rnames)
        logger.debug(
            "name=%r, geometry=%r, wavelength=%r",
            name,
            self.solver.geometry,
            wavelength,
        )
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
        self.sample.reflections.add(refl)
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
                raise OperationsError(f"Sample {name=!r} already defined.")
        lattice = Lattice(a, b, c, alpha, beta, gamma, digits)
        self._samples[name] = Sample(self, name, lattice)
        self.sample = name
        if self.solver is not None:
            self.solver.sample = self._samples[name]
        return self._samples[name]

    def assign_axes(
        self, pseudos: list[str], reals: list[str], extras: list[str]
    ) -> None:
        """
        Designate attributes for use by the PseudoPositioner class.

        Result is re-definition of 'self.axes_xref'.
        """
        pseudos = pseudos or []
        reals = reals or []
        extras = extras or []

        def itemize(label, select, full):
            keys = [name for name, _obj in full]
            for attr in select:
                if attr not in keys:
                    raise KeyError(f"Unknown {label}={attr!r}.  Known: {keys!r}")
            return keys

        def reference(dnames, snames):
            for dname, sname in zip(dnames, snames):
                self.axes_xref[dname] = sname
                both_p_r.remove(dname)

        # check for duplicates
        if len(set(pseudos + reals + extras)) != len(pseudos + reals + extras):
            raise ValueError("Axis name cannot be in more than list.")

        dfrct = self.diffractometer
        solver = dfrct.operator.solver
        if solver is None:
            return  # such as initialization

        all_pseudos = itemize("pseudo", pseudos, dfrct._get_pseudo_positioners())
        all_reals = itemize("real", reals, dfrct._get_real_positioners())
        both_p_r = all_pseudos + all_reals

        self.axes_xref = {}
        reference(pseudos, solver.pseudo_axis_names)
        reference(reals, solver.real_axis_names)
        reference(extras, solver.extra_axis_names)
        logger.debug("axes_xref=%r", self.axes_xref)

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
        return {v: k for k, v in self.axes_xref.items()}

    def auto_assign_axes(self):
        """
        Automatically assign diffractometer axes to this solver.

        .. note:: The ordered lists of axes names **could change**
           when the |solver|, or any of its settings, such as `mode`,
           are changed.  The lists are defined by the |solver| library.

           .. seealso:: Each |solver| provides ordered lists of the
              names it expects:

              * :attr:`~hklpy2.backends.base.SolverBase.extra_axis_names`
              * :attr:`~hklpy2.backends.base.SolverBase.pseudo_axis_names`
              * :attr:`~hklpy2.backends.base.SolverBase.real_axis_names`
        """

        def get_keys(getter):
            return [name for name, _obj in getter]

        def lister(dnames, snames):
            items = dnames[: len(snames)]  # first ones expected by the solver
            for dname in items:
                both_p_r.remove(dname)
            return items

        all_pseudos = get_keys(self.diffractometer._get_pseudo_positioners())
        all_reals = get_keys(self.diffractometer._get_real_positioners())
        both_p_r = all_pseudos + all_reals

        solver = self.diffractometer.operator.solver
        pseudos = lister(all_pseudos, solver.pseudo_axis_names)
        reals = lister(all_reals, solver.real_axis_names)
        extras = lister(both_p_r, solver.extra_axis_names)

        self.assign_axes(pseudos, reals, extras)

        logger.debug("axes_xref=%r", self.axes_xref)

    def calcUB(self, r1: [Reflection, str], r2: [Reflection, str]):
        """
        Calculate the UB matrix with two reflections.

        The method of Busing & Levy, Acta Cryst 22 (1967) 457.
        """

        def get_reflection(r):
            if isinstance(r, Reflection):
                return r
            reflection = self.sample.reflections.get(r)
            if reflection is None:
                raise KeyError(
                    f"Reflection {reflection!r} unknown."
                    f"  Knowns: {list(self.sample.reflections)!r}"
                )
            return reflection

        self.solver.calculateOrientation(get_reflection(r1), get_reflection(r2))
        self.sample.U = self.solver.U
        self.sample.UB = self.solver.UB
        print(f"=========> {self.sample.UB=!r}")

    def forward(self, pseudos: tuple) -> list:
        """Compute [{names:reals}] from {names: pseudos} (hkl -> angles)."""
        logger.debug(
            "(%s) forward(): pseudos=%r",
            self.__class__.__name__,
            pseudos,
        )
        # convert namedtuple to dict
        pdict = dict(zip(pseudos._fields, list(pseudos)))
        reals = {  # Original values.
            axis[0]: 0 
            for axis in self.diffractometer._get_real_positioners()
        }
        forwards = self.solver.forward(self._axes_names_d2s(pdict))
        solutions = []
        for solution in forwards:
            reals.update(self._axes_names_s2d(solution))  # Update with new values.
            solutions.append(self.diffractometer.RealPosition(**reals))
        return solutions

    def inverse(self, reals) -> dict:
        """Compute (pseudos) from {names: reals} (angles -> hkl)."""
        logger.debug(
            "(%s) inverse(): reals=%r",
            self.__class__.__name__,
            reals,
        )
        # fmt: off
        pseudos = {  # Original values.
                axis[0]: 0 
                for axis in self.diffractometer._get_pseudo_positioners()
        }
        # fmt: on
        if self.solver is None:
            # Called from the constructor before solver is defined.
            return pseudos  # current values of pseudos

        # Remove reals not used by the solver
        # and write dictionary in order expected by the solver.
        reals = self.standardize_reals(
            reals,
            self.diffractometer.real_axis_names,
        )

        # transform: reals -> pseudos
        try:
            spdict = self.solver.inverse(self._axes_names_d2s(reals))
        except Exception as excuse:
            print(f"{excuse=!r}")
            raise excuse

        pseudos.update(self._axes_names_s2d(spdict))  # Update with new values.
        return pseudos

    def remove_sample(self, name):
        """Remove the named sample.  No error if name is not known."""
        if name in self.samples:
            self._samples.pop(name)

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
        self._solver.sample = self.sample
        self._solver.wavelength = self.diffractometer.wavelength.get()
        return self._solver

    def _solver_setup(self):
        """Setup the backend |solver| for a transaction."""
        self.solver.sample = self.sample

    def standardize_pseudos(
        self,
        pseudos: list[str],
        expected: list[str] = None,
    ) -> dict[str, str]:
        """
        Convert user-supplied pseudos into dictionary.

        User could provide pseudos in several forms:

        * dict: {"h": 0, "k": 1, "l": -1}
        * namedtuple: (h=0.0, k=1.0, l=-1.0)
        * ordered list: [0, 1, -1]  (for h, k, l)
        * ordered tuple: (0, 1, -1)  (for h, k, l)
        """
        expected = expected or self.solver.pseudo_axis_names
        if len(pseudos) != len(expected):
            raise ValueError(
                f"Expected {len(expected)} pseudos, received {len(pseudos)}."
            )

        pdict = {}
        if isinstance(pseudos, dict):  # convert dict to ordered dict
            for k in expected:
                if k not in pseudos:
                    raise OperationsError(f"Missing axis {k!r}. Expected: {expected!r}")
                pdict[k] = pseudos[k]

        elif isinstance(pseudos, (list, tuple)):  # convert to ordered dict
            dnames = [
                dname
                for dname in self.axes_xref.keys()
                if dname in self.diffractometer.pseudo_axis_names
            ]
            for dname, value in zip(dnames, pseudos):
                pdict[dname] = value

        else:
            raise OperationsError(
                f"Unexpected type: {pseudos!r}.  Expected dict, list, or tuple."
            )

        return pdict

    def standardize_reals(
        self,
        reals: list[str],
        expected: list[str] = None,
    ) -> dict:
        """
        Convert user-supplied reals into dictionary.

        User could provide reals in several forms:

        * dict: {"omega": 120, "chi": 35.3, "phi": 45, "tth": -120}
        * namedtuple: (omega=120, chi=35.3, phi=45, tth=-120)
        * None: current positions
        * ordered list: [120, 35.3, 45, -120]  (for omega, chi, phi, tth)
        * ordered tuple: (120, 35.3, 45, -120)  (for omega, chi, phi, tth)
        """
        if reals is None:  # write ordered dict
            # fmt: off
            reals = [
                getattr(self.diffractometer, k).position
                for k in expected
            ]
            # fmt: on

        expected = expected or self.solver.real_axis_names
        if len(reals) != len(expected):
            raise ValueError(f"Expected {len(expected)} reals, received {len(reals)}.")

        rdict = {}
        if isinstance(reals, dict):  # convert dict to ordered dict
            for k in expected:
                if k not in reals:
                    raise OperationsError(f"Missing axis {k!r}. Expected: {reals!r}")
                rdict[k] = reals[k]

        elif isinstance(reals, (list, tuple)):  # convert to ordered dict
            dnames = [
                dname
                for dname in self.axes_xref.keys()
                if dname in self.diffractometer.real_axis_names
            ]
            for dname, value in zip(dnames, reals):
                rdict[dname] = value

        else:
            raise OperationsError(
                f"Unexpected type: {reals!r}.  Expected None, dict, list, or tuple."
            )

        return rdict

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

    @property
    def samples(self) -> dict:
        """Sample dictionary."""
        return self._samples

    @property
    def solver(self) -> SolverBase:
        """Backend |solver| object."""
        return self._solver
