"""
Wavelength of the incident radiation.

Supports compatible unit conversions.

.. autosummary::

    ~A_KEV
    ~ConstantMonochromaticWavelength
    ~MonochromaticXrayWavelength
    ~WavelengthBase
"""

import logging
from abc import ABC
from abc import abstractmethod

import pint

from .misc import WavelengthError

logger = logging.getLogger(__name__)

DEFAULT_ENERGY_UNITS = "keV"
DEFAULT_WAVELENGTH = 1.0
DEFAULT_WAVELENGTH_DEADBAND = 0.000_1
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


class WavelengthBase(ABC):
    """
    Base for all wavelength (:math:`\\lambda`) classes.

    Parameters

    units str:
        Engineering units of wavelength.  It is expected that
        wavelength and unit cell dimensions have the same units.

    .. autosummary::

        ~_fromdict
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

    def __init__(self, *, units: str = None, **kwargs):
        self._wavelength_units = units or DEFAULT_WAVELENGTH_UNITS

    def _asdict(self):
        """Return source parameters as a dict."""
        info = {
            "source_type": self.source_type,
            "wavelength_units": self.wavelength_units,
            "wavelength": self.wavelength,
        }
        if hasattr(self, "energy"):
            info.update(
                {
                    "energy_units": self.energy_units,
                    "energy": self.energy,
                }
            )
        return info

    def _fromdict_core(self, config):
        """Restore most items from config dictionary."""
        if not isinstance(config, dict):
            raise TypeError(f"Unrecognized configuration: {config!r}")
        if self.source_type != config["source_type"]:
            raise ValueError(
                f"Unexpected source type: Received ({config['source_type']!r})"
                f" Expected: {self.source_type!r}"
            )
        self.wavelength_units = config["wavelength_units"]
        if hasattr(self, "energy_units") is not None:
            self.energy_units = config.get("energy_units", DEFAULT_ENERGY_UNITS)

    def _fromdict(self, config):
        """Restore configuration from dictionary."""
        self._fromdict_core(config)
        self.wavelength = config["wavelength"]

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
        # Raise pint.DimensionalityError if not convertible to our units.
        pint.UnitRegistry().convert(1, value, DEFAULT_WAVELENGTH_UNITS)

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

    def __init__(
        self,
        wavelength: float,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._wavelength = wavelength

    def _fromdict(self, config: dict[str, (float | int | str)]):
        """Restore configuration from dictionary but not wavelength."""
        self._fromdict_core(config)

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

    Parameters

    wavelength float:
        Monochromatic wavelength of the incident radiation.  It is expected that
        wavelength and unit cell dimensions have the same units.

    units str:
        Engineering units of wavelength.  It is expected that
        wavelength and unit cell dimensions have the same units.

    wavelength_updated object:
        Caller provided function to signal when wavelength has been updated.
        Set ``True`` from ``wavelength.setter`` property.

    wavelength_deadband float:
        Variation in wavelength less than this number will not cause
        wavelength_updated to be updated.

    energy_units str:
        Engineering units of energy.

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

    def __init__(
        self,
        wavelength: float = DEFAULT_WAVELENGTH,
        energy_units: str = None,
        wavelength_updated: object = None,
        wavelength_deadband: float = DEFAULT_WAVELENGTH_DEADBAND,
        **kwargs,
    ):
        self.energy_units = energy_units or DEFAULT_ENERGY_UNITS
        self.wavelength_updated = wavelength_updated
        super().__init__(**kwargs)
        self._wavelength = wavelength
        self.wavelength_deadband = wavelength_deadband
        self.wavelength_reference = wavelength

    @property
    def wavelength(self) -> float:
        """Wavelength (:math:`\\lambda`)."""
        return self._wavelength

    @wavelength.setter
    def wavelength(self, value: float) -> None:
        self._wavelength = value
        if abs(value - self.wavelength_reference) > self.wavelength_deadband:
            if self.wavelength_updated is not None:
                self.wavelength_updated(True)
            self.wavelength_reference = value

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

        Will raise ``pint.DimensionalityError`` if not convertible to our units.
        """
        pint.UnitRegistry().convert(1, value, DEFAULT_ENERGY_UNITS)
        self._energy_units = value
