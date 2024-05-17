"""
Wavelength of the incident radiation.

Supports compatible unit conversions.

.. autosummary::

    ~A_KEV
    ~ConstantMonochromaticWavelength
    ~MonochromaticXrayWavelength
    ~WavelengthBase
    ~WavelengthError
"""

import logging
from abc import ABC
from abc import abstractmethod

import pint

from . import Hklpy2Error

logger = logging.getLogger(__name__)

DEFAULT_ENERGY_UNITS = "keV"
DEFAULT_WAVELENGTH = 1.0
DEFAULT_WAVELENGTH_UNITS = "angstrom"

XRAY_ENERGY_EQUIVALENT_ = 8.065_543_937e5
"""
Energy equivalent factor :math:`1 / (h \\nu)`

Per NIST publication, of CODATA Fundamental Physical Constants, 2022 revision.

:see: https://physics.nist.gov/cuu/Constants/factors.html ("1 eV" *v*. "1/m")
"""

A_KEV = 1e7 / XRAY_ENERGY_EQUIVALENT_  # 1 Angstrom ~= 12.39842 keV
"""
X-ray voltage wavelength product (:math:`h \\nu`), per NIST standard.
"""


class WavelengthError(Hklpy2Error):
    """Custom exceptions from the :mod:`hklpy2.wavelength_support` module."""


class WavelengthBase(ABC):
    """
    Base for all wavelength (:math:`\\lambda`) classes.

    .. autosummary::

        ~wavelength
        ~wavelength_units
        ~source_type
        ~spectrum_type
    """

    source_type = "any"
    """
    Nature of the incident radiation.
    """
    # Choices: ``any``, ``neutron``, ``X-ray``

    spectrum_type = "any"
    """
    Description of the spectrum of the incident radiation.
    """
    # Choices: ``any``, ``continuous``, ``monochromatic``, ``time-of-flight``

    def __init__(self, *, units: str = None):
        self._wavelength_units = units or DEFAULT_WAVELENGTH_UNITS

    @property
    @abstractmethod
    def wavelength(self) -> float:
        """Wavelength (:math:`\\lambda`)."""

    @property
    def wavelength_units(self) -> str:
        """Engineering units of the wavelength."""
        return self._wavelength_units

    @wavelength_units.setter
    def wavelength_units(self, value) -> None:
        if hasattr(self, "_wavelength") and hasattr(self, "_wavelength_units"):
            # When wavelength_units change, convert existing
            # wavelength value to new units.
            wavelength = pint.Quantity(self._wavelength, self._wavelength_units)
            self._wavelength = wavelength.to(value).magnitude
        self._wavelength_units = value


class ConstantMonochromaticWavelength(WavelengthBase):
    """
    Monochromatic wavelength (and units); cannot be changed.

    Just wavelength.  Can be used with any type of radiation source.

    .. autosummary::

        ~wavelength
        ~wavelength_units
        ~source_type
        ~spectrum_type
    """

    source_type = "any"
    spectrum_type = "monochromatic"

    def __init__(self, wavelength: float, **kwargs):
        super().__init__(**kwargs)
        self._wavelength = wavelength

    @property
    def wavelength(self) -> float:
        """Wavelength (:math:`\\lambda`)."""
        return self._wavelength

    @wavelength.setter
    def wavelength(self, value) -> None:
        """Wavelength."""
        raise WavelengthError("Cannot change constant wavelength.")


class MonochromaticXrayWavelength(WavelengthBase):
    """
    Monochromatic X-ray wavelength (and units).

    .. autosummary::

        ~wavelength
        ~wavelength_units
        ~energy
        ~energy_units
        ~source_type
        ~spectrum_type
    """

    source_type = "X-ray"
    spectrum_type = "monochromatic"

    def __init__(self, wavelength: float, energy_units: str = None, **kwargs):
        self.energy_units = energy_units or DEFAULT_ENERGY_UNITS
        super().__init__(**kwargs)
        self.wavelength = wavelength

    @property
    def wavelength(self) -> float:
        """Wavelength (:math:`\\lambda`)."""
        return self._wavelength

    @wavelength.setter
    def wavelength(self, value: float) -> None:
        self._wavelength = value

    @property
    def energy(self) -> float:
        """
        Incident monochromatic X-ray photon energy (:math:`E`).

        .. math::

            \\lambda = (h \\nu) / E

        """
        wavelength = pint.Quantity(self.wavelength, self.wavelength_units)
        wavelength = wavelength.to(DEFAULT_WAVELENGTH_UNITS).magnitude
        energy = pint.Quantity(A_KEV / wavelength, DEFAULT_ENERGY_UNITS)
        return energy.to(self.energy_units).magnitude

    @energy.setter
    def energy(self, value: float) -> None:
        energy = pint.Quantity(value, self.energy_units)
        energy = energy.to(DEFAULT_ENERGY_UNITS).magnitude
        wavelength = pint.Quantity(A_KEV / energy, DEFAULT_WAVELENGTH_UNITS)
        self.wavelength = wavelength.to(self.wavelength_units).magnitude

    @property
    def energy_units(self) -> str:
        """
        Engineering units of the X-ray photon energy.
        """
        return self._energy_units

    @energy_units.setter
    def energy_units(self, value) -> None:
        """
        Engineering units of the X-ray photon energy.
        """
        if hasattr(self, "_energy") and hasattr(self, "_energy_units"):
            # Convert existing energy value to new units.
            energy = pint.Quantity(self._energy, self._energy_units)
            self._energy = energy.to(value).magnitude
        self._energy_units = value
