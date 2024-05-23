"""
Operate the diffractometer using a |solver| library and geometry.

Intermediate layer between DiffractometerBase Device and backend |solver|
library.

.. autosummary::

    ~SolverOperator
"""

import logging

from . import Hklpy2Error
from . import SolverBase
from .lattice import Lattice
from .misc import solver_factory
from .sample import Sample

__all__ = "SolverOperator SolverOperatorError".split()
logger = logging.getLogger(__name__)


class SolverOperatorError(Hklpy2Error):
    """Custom exceptions from :class:`~SolverOperator`."""


class SolverOperator:
    """
    Operate the diffractometer using a |solver|.

    Parameters

    - ``solver`` str: Name of the backend |solver| library.
    - ``geometry`` str: Name of the backend |solver| geometry.

    .. rubric:: Python Methods

    .. autosummary::

        ~add_sample
        ~auto_assign_axes
        ~check_solver_defined
        ~forward
        ~inverse
        ~remove_sample
        ~set_solver

    .. rubric:: Python Properties

    .. autosummary::

        ~geometry
        ~sample
        ~solver
    """

    def __init__(self, diffractometer, default_sample: bool = True) -> None:
        self.diffractometer = diffractometer
        self._sample_name = None
        self._samples = {}
        self._solver = None
        self.axes_xref = {}  # axes names cross-reference: diffractometer: solver

        if default_sample:
            # first sample is cubic, no reflections
            self.add_sample("cubic", 1)

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
                raise SolverOperatorError(f"Sample {name=!r} already defined.")
        lattice = Lattice(a, b, c, alpha, beta, gamma, digits)
        self._samples[name] = Sample(name, lattice)
        self.sample = name
        return self._samples[name]

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

        Example::

            >>> fourc.operator.solver
            HklSolver(name='hkl_soleil', version='v5.0.0.3434', geometry='E4CV', engine='hkl', mode='bissector')
            >>> fourc.operator.real_axis_names
            ['omega', 'chi', 'phi', 'tth']
            >>> fourc.operator.auto_assign_axes()
            >>> fourc.operator.axes_xref
            {'h': 'h', 'k': 'k', 'l': 'l', 'theta': 'omega', 'chi': 'chi', 'phi': 'phi', 'ttheta': 'tth'}
        """
        self.axes_xref = {}
        for space in "pseudo real extra".split():
            if space == "extra":
                dnames = (
                    self.diffractometer.pseudo_axis_names
                    + self.diffractometer.real_axis_names
                )
            else:
                dnames = getattr(self.diffractometer, f"{space}_axis_names")
            pnames = getattr(self.solver, f"{space}_axis_names")
            np = len(pnames)
            if len(dnames) < np:
                raise SolverOperatorError(f"Need these {space} axes: {pnames!r}")
            for dname, pname in zip(dnames, pnames):
                self.axes_xref[dname] = pname

    def check_solver_defined(self):
        """Raise DiffractometerError if solver is not defined."""
        if self.solver is None:
            # TODO: First try to create a new solver.
            raise SolverOperatorError("Call 'set_solver()' first.")

    def forward(self, pseudos) -> list:
        """Compute [{names:reals}] from {names: pseudos} (hkl -> angles)."""
        logger.debug(
            "(%s) forward(): pseudos=%r",
            self.__class__.__name__,
            pseudos,
        )
        # TODO: self.check_solver_defined()
        axes = self.diffractometer._get_real_positioners()  # TODO:
        reals = {axis[0]: 0 for axis in axes}
        return [reals]

    def inverse(self, reals) -> dict:
        """Compute (pseudos) from {names: reals} (angles -> hkl)."""
        logger.debug(
            "(%s) inverse(): reals=%r",
            self.__class__.__name__,
            reals,
        )
        # TODO: self.check_solver_defined()
        axes = self.diffractometer._get_pseudo_positioners()  # TODO:
        pseudos = {axis[0]: 0 for axis in axes}
        return pseudos

    def remove_sample(self, name):
        """Remove the named sample.  No error if name is not known."""
        if name in self.samples:
            self._samples.pop(name)

    def set_solver(
        self,
        name: str,
        geometry: str,
        pseudos: list = [],  # TODO:
        reals: list = [],  # TODO:
        extras: list = [],  # TODO:
        **kwargs: dict,
    ) -> SolverBase:
        """
        Create an instance of the |solver| and geometry.

        Parameters

        - ``solver`` str: Name of the backend |solver| library.
        - ``geometry`` str: Name of the backend |solver| geometry.
        - ``kwargs`` dict: Keyword arguments, as needed by the chosen |solver|.
        """
        logger.debug(
            "(%s) solver=%r, geometry=%r, pseudos=%r, reals=%r, extras=%r, kwargs=%r",
            self.__class__.__name__,
            name,
            geometry,
            pseudos,
            reals,
            extras,
            kwargs,
        )
        self._solver = solver_factory(name, geometry, **kwargs)
        return self._solver

    # ---- get/set properties

    @property
    def geometry(self) -> str:
        """Backend |solver| geometry name."""
        self.check_solver_defined()
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
