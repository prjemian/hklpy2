"""
Base class for all diffractometers

.. autosummary::

    ~DiffractometerBase
"""

import logging

from ophyd import Component as Cpt
from ophyd import PseudoPositioner
from ophyd.signal import AttributeSignal

from .wavelength_support import DEFAULT_WAVELENGTH
from .wavelength_support import ConstantMonochromaticWavelength

__all__ = ["DiffractometerBase"]
logger = logging.getLogger(__name__)

DEFAULT_PHOTON_ENERGY_KEV = 8.0


class DiffractometerBase(PseudoPositioner):
    """
    Base class for all diffractometers.

    .. rubric:: (ophyd) Components

    .. autosummary::

        ~solver
        ~wavelength

    .. rubric:: Python Methods

    .. rubric:: Python Properties

    .. autosummary::

        ~backend_solver
    """

    # TODO: allow for extra pseudos and reals
    # Allow the subclass to provide more axes than required.
    # Also allow axes to be renamed.
    # Needs a way to specify which ones used with particular solver.

    # These two attributes are used by the PseudoPositioner class.
    # _pseudo = []  # List of pseudo-space PseudoPositioner objects.
    # _real = []  # List of real-space positioner objects.

    # ophyd Device Components

    # ophyd Device Attribute Components

    # TODO: need a solver object AND a solver name
    solver = Cpt(
        AttributeSignal,
        attr="backend_solver",
        doc="Name of backend |solver| (library).",
        write_access=True,
    )
    """Name of backend |solver| (library)."""

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

    def __init__(self, *args, **kwargs):
        self._backend_solver = None
        self._wavelength = ConstantMonochromaticWavelength(DEFAULT_WAVELENGTH)

        super().__init__(*args, **kwargs)

    # ---- get/set properties

    @property
    def backend_solver(self):
        """Backend |solver|, transformations between pseudos and reals."""
        # TODO: self._backend_solver should be instance of a |solver| class.
        # return its name (if it is not None)
        # TODO: backend_solver v. backend_solver_name
        return self._backend_solver

    @backend_solver.setter
    def backend_solver(self, value: str):
        # TODO: self._backend_solver should be instance of a |solver| class.
        # TODO: backend_solver v. backend_solver_name
        self._backend_solver = value
