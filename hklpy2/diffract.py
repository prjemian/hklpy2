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

__all__ = ["DiffractometerBase"]
logger = logging.getLogger(__name__)


class DiffractometerBase(PseudoPositioner):
    """
    Base class for all diffractometers.

    .. autosummary::

        ~solver
        ~energy
        ~energy_units
        ~energy_offset
    """

    # _pseudo = []
    # """List of pseudo-space PseudoPositioner objects."""

    # _real = []
    # """List of real-space positioner objects."""

    solver = Cpt(Signal, value=None, doc="backend library")
    """Connects Diffractometer with a backend Solver (library)."""

    _wavelength = None
    wavelength = Cpt(
        AttributeSignal,
        attr="_wavelength",
        doc="incident wavelength, (angstrom)",
        write_access=False,
    )

    energy = Cpt(Signal, value=8.0, doc="monochromatic X-ray photon energy")
    """
    Incoming monochromatic X-ray photon energy (:math:`E`).

    .. math::

        \\lambda = (h \\nu) / (E + \\Delta E)
    """

    energy_units = Cpt(Signal, value="keV")
    """Engineering units of photon energy."""

    energy_offset = Cpt(Signal, value=0)
    """X-ray photon energy adjustment constant (:math:`\\Delta E`)."""

    # energy_update_calc_flag = Cpt(Signal, value=True)
    # """internal use"""
