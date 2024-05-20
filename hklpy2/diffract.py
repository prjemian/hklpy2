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
from .misc import UNDEFINED
from .misc import solver_factory
from .misc import solvers
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

    .. rubric:: (ophyd) Components

    .. rubric :: (ophyd) Attribute Components

    .. autosummary::

        ~solver
        ~geometry
        ~wavelength
        ~wavelength_units

    .. rubric:: Python Methods

    .. rubric:: Python Properties

    .. autosummary::

        ~geometry_name
        ~solver_name
    """

    # TODO: allow for extra pseudos and reals
    # Allow the subclass to provide more axes than required.
    # Also allow axes to be renamed.
    # Needs a way to specify which ones used with particular solver.

    # These two attributes are used by the PseudoPositioner class.
    # _pseudo = []  # List of pseudo-space PseudoPositioner objects.
    # _real = []  # List of real-space positioner objects.

    # TODO: need a solver object AND a solver name
    solver = Cpt(
        AttributeSignal,
        attr="solver_name",
        doc="Name of backend |solver| (library).",
        write_access=True,
    )
    """Name of backend |solver| (library)."""

    geometry = Cpt(
        AttributeSignal,
        attr="geometry_name",
        doc="Name of backend |solver| geometry.",
        write_access=True,
    )
    """Name of backend |solver| geometry."""

    wavelength = Cpt(
        AttributeSignal,
        attr="_wavelength.wavelength",
        doc="incident wavelength, (angstrom)",
        write_access=False,
    )
    """Incident wavelength."""

    wavelength_units = Cpt(
        AttributeSignal,
        attr="_wavelength.wavelength_units",
        doc="engineering units of the incident wavelength",
        write_access=False,
    )
    """Engineering units of the incident wavelength."""

    def __init__(
        self,
        *args,
        solver: str = None,
        geometry: str = None,
        **kwargs,
    ):
        if solver is None:
            self._solver = UNDEFINED
        else:
            self.solver_name = solver
        if geometry is not None:
            self.geometry_name = geometry
        self._wavelength = ConstantMonochromaticWavelength(DEFAULT_WAVELENGTH)

        super().__init__(*args, **kwargs)

    @pseudo_position_argument
    def forward(self, pseudos: dict):
        """Compute tuple of reals from pseudos (hkl -> angles)."""
        return tuple((0, 0, 0, 0, 0, 0, 0, 0, 0, 0))  # FIXME

    @real_position_argument
    def inverse(self, reals: dict):
        """Compute tuple of pseudos from reals (angles -> hkl)."""
        return tuple((0, 0, 0, 0, 0, 0, 0, 0, 0, 0))  # FIXME

    # ---- get/set properties

    @property
    def geometry_name(self):
        """Backend |solver| geometry name."""
        if self.solver_name == "":
            return ""
        return self._solver.geometry

    @geometry_name.setter
    def geometry_name(self, value: str):
        if self.solver_name == "":
            raise DiffractometerError("First, define the solver.")
        self._solver.geometry = value

    @property
    def solver_name(self):
        """Backend |solver| library name."""
        if self._solver == UNDEFINED:
            return ""
        return self._solver.name

    @solver_name.setter
    def solver_name(self, value: str):
        if value == UNDEFINED:
            raise DiffractometerError(
                f"Pick one of these solver names: {list(solvers())!r}"
            )
        self._solver = solver_factory(value, geometry=UNDEFINED)
