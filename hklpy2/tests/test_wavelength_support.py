import math

import pytest

from ..wavelength_support import DEFAULT_ENERGY_UNITS
from ..wavelength_support import DEFAULT_WAVELENGTH_UNITS
from ..wavelength_support import ConstantMonochromaticWavelength
from ..wavelength_support import MonochromaticXrayWavelength
from ..wavelength_support import WavelengthError


def test_ConstantMonochromaticWavelength():
    wl = ConstantMonochromaticWavelength(1.0)
    assert wl is not None
    assert math.isclose(wl.wavelength, 1.0, abs_tol=0.001)
    assert wl.wavelength_units == DEFAULT_WAVELENGTH_UNITS

    assert "nm" != DEFAULT_WAVELENGTH_UNITS
    wl.wavelength_units = "nm"
    assert wl.wavelength_units == "nm"
    assert math.isclose(wl.wavelength, 0.1, abs_tol=0.000_1)

    with pytest.raises(WavelengthError) as reason:
        wl.wavelength = 2.0  # try to change it
    assert "Cannot change constant" in str(reason)


@pytest.mark.parametrize(
    "wavelength, wunits, energy, eunits, tol",
    [
        [1, None, 12.4, "keV", 0.1],
        [1, None, 12.4, None, 0.1],
        [1, "angstrom", 12.4, "keV", 0.1],
        [100, "pm", 12.4, "keV", 0.1],
        [100, "pm", 12398.4, "eV", 0.1],
        [0.1, "nm", 12.4, "keV", 0.1],
        [100, "nm", 12.4, "eV", 0.1],
        [0.1, "um", 12.4, "eV", 0.1],
    ],
)
def test_MonochromaticXrayWavelength_set_w(wavelength, wunits, energy, eunits, tol):
    wl = MonochromaticXrayWavelength(wavelength, units=wunits)
    assert wl.wavelength_units == wunits or DEFAULT_WAVELENGTH_UNITS
    assert math.isclose(wl.wavelength, wavelength, rel_tol=0.01)
    wl.energy_units = eunits or DEFAULT_ENERGY_UNITS
    assert math.isclose(wl.energy, energy, abs_tol=tol), f"{wl.energy=!r}"


def test_MonochromaticXrayWavelength_change_units():
    wavelength = 1.0
    rtol = 0.001
    wl = MonochromaticXrayWavelength(1.0, units="angstrom")
    assert wl.wavelength_units == "angstrom"
    assert math.isclose(wl.wavelength, wavelength, rel_tol=rtol)
    assert math.isclose(wl.energy, 12.39842, rel_tol=rtol)

    wl.wavelength_units = "pm"
    assert math.isclose(wl.wavelength, 100 * wavelength, rel_tol=rtol)
    assert math.isclose(wl.energy, 12.39842, rel_tol=rtol)

    wl.wavelength_units = "nm"
    assert math.isclose(wl.wavelength, 0.1 * wavelength, rel_tol=rtol)
    assert math.isclose(wl.energy, 12.39842, rel_tol=rtol)

    wl.energy_units = "eV"
    assert math.isclose(wl.wavelength, 0.1 * wavelength, rel_tol=rtol)
    assert math.isclose(wl.energy, 12398.42, rel_tol=rtol)
