"""
Base class for all diffractometers

.. autosummary::

    ~DiffractometerBase
"""

import logging

from ophyd import Component as Cpt
from ophyd import PseudoPositioner
from ophyd import Signal
from ophyd.signal import AttributeSignal

from .misc import A_KEV

__all__ = ["DiffractometerBase"]
logger = logging.getLogger(__name__)

DEFAULT_PHOTON_ENERGY_KEV = 8.0


class DiffractometerBase(PseudoPositioner):
    """
    Base class for all diffractometers.

    .. autosummary::

        ~solver
        ~wavelength
        ~energy
        ~energy_units
        ~energy_offset
    """

    # _pseudo = []
    # """List of pseudo-space PseudoPositioner objects."""

    # _real = []
    # """List of real-space positioner objects."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._backend_solver = None

    solver = Cpt(
        AttributeSignal,
        attr="_solver",
        doc="Name of backend |solver| (library).",
        write_access=True,
    )
    """Name of backend |solver| (library)."""

    # TODO: Refactor as a class.  Could be changed more easily.
    # To support other incident beam sources, such as neutron TOF,
    # handle wavelength with a class.
    _wavelength = A_KEV / DEFAULT_PHOTON_ENERGY_KEV
    wavelength = Cpt(
        AttributeSignal,
        attr="_wavelength",
        doc="incident wavelength, (angstrom)",
        write_access=False,
    )
    """Incident wavelength, (angstrom)."""

    # fmt: off
    energy = Cpt(
        Signal, value=DEFAULT_PHOTON_ENERGY_KEV,
        doc="monochromatic X-ray photon energy"
    )
    """
    Incoming monochromatic X-ray photon energy (:math:`E`).

    .. math::

        \\lambda = (h \\nu) / (E + \\Delta E)
    """
    # fmt: on

    energy_units = Cpt(Signal, value="keV")
    """Engineering units of photon energy."""

    energy_offset = Cpt(Signal, value=0)
    """X-ray photon energy adjustment constant (:math:`\\Delta E`)."""

    # energy_update_calc_flag = Cpt(Signal, value=True)
    # """internal use"""

    # ---- get/set properties

    @property
    def _solver(self):
        """Backend |solver|, transformations between pseudos and reals."""
        return self._backend_solver

    @_solver.setter
    def _solver(self, value: str):
        self._backend_solver = value
