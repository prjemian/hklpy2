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
from .misc import solver_factory
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

        ~wavelength
        ~wavelength_units

    .. rubric:: Python Methods

    .. autosummary::

        ~forward
        ~inverse
        ~set_solver

    .. rubric:: Python Properties

    .. autosummary::

        ~geometry_name
        ~solver_name
    """

    # These two attributes are used by the PseudoPositioner class.
    # _pseudo = []  # List of pseudo-space PseudoPositioner objects.
    # _real = []  # List of real-space positioner objects.

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
        **kwargs,
    ):
        self._solver = None
        self._wavelength = ConstantMonochromaticWavelength(DEFAULT_WAVELENGTH)

        super().__init__(*args, **kwargs)

    @pseudo_position_argument
    def forward(self, pseudos: dict):
        """Compute tuple of reals from pseudos (hkl -> angles)."""
        # TODO: have the solver handle this, from the pseudos
        print(f"forward(): {pseudos=!r}")
        pos = {axis[0]: 0 for axis in self._get_real_positioners()}
        return self.RealPosition(**pos)

    @real_position_argument
    def inverse(self, reals: dict):
        """Compute tuple of pseudos from reals (angles -> hkl)."""
        # TODO: have the solver handle this, from the reals
        print(f"inverse(): {reals=!r}")
        pos = {axis[0]: 0 for axis in self._get_pseudo_positioners()}
        return self.PseudoPosition(**pos)

    def set_solver(self, solver: str, geometry: str, **kwargs):
        """Set the backend |solver| for this diffracometer."""
        self._solver = solver_factory(solver, geometry=geometry, **kwargs)

    # ---- get/set properties

    @property
    def geometry_name(self):
        """Backend |solver| geometry name."""
        if self._solver is not None:
            return self._solver.geometry
        return ""

    @property
    def solver_name(self):
        """Backend |solver| library name."""
        if self._solver is not None:
            return self._solver.name
        return ""
