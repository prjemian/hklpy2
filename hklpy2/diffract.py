"""
Base class for all diffractometers

.. autosummary::

    ~DiffractometerBase
"""

import logging

from ophyd import Component as Cpt
from ophyd import PseudoPositioner
from ophyd.pseudopos import pseudo_position_argument
from ophyd.pseudopos import real_position_argument
from ophyd.signal import AttributeSignal

from . import Hklpy2Error
from .ops import SolverOperator
from .wavelength_support import DEFAULT_WAVELENGTH
from .wavelength_support import ConstantMonochromaticWavelength
from .sample import Sample

__all__ = ["DiffractometerBase"]
logger = logging.getLogger(__name__)

DEFAULT_PHOTON_ENERGY_KEV = 8.0


class DiffractometerError(Hklpy2Error):
    """Custom exceptions from a :class:`~DiffractometerBase` subclass."""


class DiffractometerBase(PseudoPositioner):
    """
    Base class for all diffractometers.

    .. rubric:: (ophyd) Components

    .. rubric :: (ophyd) Attribute Components

    .. autosummary::

        ~geometry
        ~solver
        ~wavelength

    .. rubric:: Python Methods

    .. autosummary::

        ~add_sample
        ~choose_first_forward_solution
        ~forward
        ~inverse
        ~set_solver

    .. rubric:: Python Properties

    .. autosummary::

        ~sample
        ~samples
        ~solver_name
    """

    # These two attributes are used by the PseudoPositioner class.
    # _pseudo = []  # List of pseudo-space PseudoPositioner objects.
    # _real = []  # List of real-space positioner objects.

    geometry = Cpt(
        AttributeSignal,
        attr="operator.geometry",
        doc="Name of backend |solver| geometry.",
        write_access=False,
        kind="config",
    )
    """Name of backend |solver| geometry."""

    solver = Cpt(
        AttributeSignal,
        attr="solver_name",
        doc="Name of backend |solver| (library).",
        write_access=False,
        kind="config",
    )
    """Name of backend |solver| (library)."""

    wavelength = Cpt(
        AttributeSignal,
        attr="_wavelength.wavelength",
        doc="Wavelength of incident radiation.",
        write_access=True,
        kind="config",
    )
    """Wavelength of incident radiation."""

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        self._backend = None
        self._wavelength = ConstantMonochromaticWavelength(DEFAULT_WAVELENGTH)
        self.operator = SolverOperator(self)
        self._forward_solution = self.choose_first_forward_solution

        super().__init__(*args, **kwargs)

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
    ) -> Sample:
        """Add a new sample."""
        return self.operator.add_sample(
            name,
            a,
            b,
            c,
            alpha,
            beta,
            gamma,
            digits,
        )

    def choose_first_forward_solution(self, solutions: list):
        """
        Choose first solution from list returned by '.forward()'.

        User can provide an alternative function and assign to
        'self._forward_solution'.
        """
        return solutions[0]

    @pseudo_position_argument
    def forward(self, pseudos: dict) -> tuple:
        """Compute real-space coordinates from pseudos (hkl -> angles)."""
        solutions = self.operator.forward(pseudos)
        pos = self._forward_solution(solutions)
        return self.RealPosition(**pos)  # as created by namedtuple

    @real_position_argument
    def inverse(self, reals: dict) -> tuple:
        """Compute pseudo-space coordinates from reals (angles -> hkl)."""
        pos = self.operator.inverse(reals)
        return self.PseudoPosition(**pos)  # as created by namedtuple

    def set_solver(self, solver: str, geometry: str, **kwargs: dict):
        """Set the backend |solver| for this diffractometer."""
        self.operator.set_solver(solver, geometry, **kwargs)

    # ---- get/set properties

    @property
    def samples(self):
        """Dictionary of samples."""
        if self.operator is None:
            return {}
        return self.operator.samples

    @property
    def sample(self):
        """Current sample object."""
        if self.operator is None:
            return None
        return self.operator.sample

    @sample.setter
    def sample(self, value: str) -> None:
        self.operator.sample = value

    @property
    def solver_name(self):
        """Backend |solver| library name."""
        if self.operator is not None and self.operator.solver is not None:
            return self.operator.solver.name
        return ""
