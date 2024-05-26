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
from .operations.sample import Sample
from .ops import SolverOperator
from .wavelength_support import DEFAULT_WAVELENGTH
from .wavelength_support import ConstantMonochromaticWavelength

__all__ = ["DiffractometerBase"]
logger = logging.getLogger(__name__)

DEFAULT_PHOTON_ENERGY_KEV = 8.0


class DiffractometerError(Hklpy2Error):
    """Custom exceptions from a :class:`~DiffractometerBase` subclass."""


class DiffractometerBase(PseudoPositioner):
    """
    Base class for all diffractometers.

    .. rubric:: Parameters

    *   ``solver`` (*str*) : Name of |solver| library.
        (default: unspecified)
    *   ``geometry``: (*str*) : Name of |solver| geometry.
        (default: unspecified)
    *   ``solver_kwargs`` (*dict*) : Any additional keyword arguments needed
        by |solver| library. (default: empty)
    *   ``pseudos`` ([str]) : List of diffractometer axis names to be used
        as pseudo axes. (default: unspecified)
    *   ``reals`` ([str]) : List of diffractometer axis names to be used as
        real axes. (default: unspecified)
    *   ``extras`` ([str]) : List of diffractometer axis names to be used as
        extra axes. (default: unspecified)

    .. rubric:: (ophyd) Components

    .. rubric :: (ophyd) Attribute Components

    .. autosummary::

        ~geometry
        ~solver
        ~wavelength

    .. rubric:: Python Methods

    .. autosummary::

        ~add_reflection
        ~add_sample
        ~auto_assign_axes
        ~choose_first_forward_solution
        ~forward
        ~inverse
        ~set_solver

    .. rubric:: Python Properties

    .. autosummary::

        ~pseudo_axis_names
        ~real_axis_names
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
        solver: str = None,
        geometry: str = None,
        solver_kwargs: dict = {},
        pseudos: list[str] = None,
        reals: list[str] = None,
        extras: list[str] = None,
        **kwargs,
    ):
        self._backend = None
        self._wavelength = ConstantMonochromaticWavelength(DEFAULT_WAVELENGTH)
        self.operator = SolverOperator(self)
        self._forward_solution = self.choose_first_forward_solution

        super().__init__(*args, **kwargs)

        if isinstance(solver, str) and isinstance(geometry, str):
            self.set_solver(solver, geometry, **solver_kwargs)

        self.operator.assign_axes(pseudos, reals, extras)

    def add_reflection(self, pseudos, reals=None, wavelength=None, name=None):
        """
        Add a new reflection with this geometry to the selected sample.

        .. rubric:: Parameters

        * ``pseudos`` (various): pseudo-space axes and values.
        * ``reals`` (various): dictionary of real-space axes and values.
        * ``wavelength`` (float): Wavelength of incident radiation.
          If ``None``, diffractometer's current wavelength will be assigned.
        * ``name`` (str): Reference name for this reflection.
          If ``None``, a random name will be assigned.
        """
        self.operator.add_reflection(
            pseudos, reals, wavelength or self.wavelength.get(), name
        )

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
        return self.operator.add_sample(
            name,
            a,
            b,
            c,
            alpha,
            beta,
            gamma,
            digits,
            replace,
        )

    def auto_assign_axes(self):
        """
        Automatically assign diffractometer axes to this solver.

        .. seealso:: :meth:`hklpy2.ops.SolverOperator.auto_assign_axes`

        A |solver| geometry specifies expected pseudo, real, and extra axes
        for its ``.forward()`` and ``.inverse()`` coordinate transformations.

        This method assigns this diffractometer's:

        *   first PseudoSingle axes
            to the pseudo axes expected by the selected |solver|.
        *   first Positioner axes (or subclass,
            such as EpicsMotor or SoftPositioner) to the real axes expected
            by the selected |solver|.
        *   any remaining PseudoSingle and Positioner axes to the
            extra axes expected by the selected |solver|.

        Any diffractometer axes not expected by the |solver| will
        not be assigned.
        """
        self.operator.auto_assign_axes()

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
        """
        Set the backend |solver| for this diffractometer.

        .. rubric:: Parameters

        * ``solver`` (str): Name of the |solver| library.
        * ``geometry`` (str): Name of the |solver| geometry.
        * ``kwargs`` (dict): Any keyword arguments needed by the |solver|.
        """
        self.operator.set_solver(solver, geometry, **kwargs)

    # ---- get/set properties

    @property
    def pseudo_axis_names(self):
        """
        Names of all the pseudo axes, in order of appearance.

        Example::

            >>> fourc.pseudo_axis_names
            ['h', 'k', 'l']
        """
        return [o.attr_name for o in self.pseudo_positioners]

    @property
    def real_axis_names(self):
        """
        Names of all the real axes, in order of appearance.

        Example::

            >>> fourc.real_axis_names
            ['omega', 'chi, 'phi', 'tth']
        """
        return [o.attr_name for o in self.real_positioners]

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
