import math
from contextlib import nullcontext as does_not_raise

import pytest

from ..beam import DEFAULT_ENERGY_UNITS
from ..beam import DEFAULT_WAVELENGTH_DEADBAND
from ..beam import DEFAULT_WAVELENGTH_UNITS
from ..beam import ConstantMonochromaticWavelength
from ..beam import MonochromaticXrayWavelength
from ..misc import WavelengthError
from .common import assert_context_result


@pytest.mark.parametrize(
    "context, expected",
    [
        [pytest.raises(WavelengthError), "Cannot change constant"],
    ],
)
def test_ConstantMonochromaticWavelength(context, expected):
    wl = ConstantMonochromaticWavelength(1.0)
    assert wl is not None
    assert math.isclose(wl.wavelength, 1.0, abs_tol=0.001)
    assert wl.wavelength_units == DEFAULT_WAVELENGTH_UNITS

    assert "nm" != DEFAULT_WAVELENGTH_UNITS
    wl.wavelength_units = "nm"
    assert wl.wavelength_units == "nm"
    assert math.isclose(wl.wavelength, 0.1, abs_tol=0.000_1)

    with context as reason:
        wl.wavelength = 2  # try to change it
    assert_context_result(expected, reason)


@pytest.mark.parametrize(
    "info, context, expected",
    [
        [
            {
                "source_type": "any",
                "wavelength_units": "angstrom",
                "wavelength": 1.0,
            },
            does_not_raise(),
            None,
        ],
        [
            {
                "source_type": "any",
                "wavelength_units": "angstrom",
                "wavelength": 2,
            },
            does_not_raise(),
            None,
        ],
        [
            "not a dict",
            pytest.raises(TypeError),
            "Unrecognized configuration: 'not a dict'",
        ],
        [
            {
                "source_type": "torch",
                "wavelength_units": "um",
                "wavelength": 0.5,
            },
            pytest.raises(ValueError),
            "Unexpected source type: Received",
        ],
    ],
)
def test_ConstantMonochromaticWavelength_restore(info, context, expected):
    with context as reason:
        wl = ConstantMonochromaticWavelength(1.0)
        wl._fromdict(info)
    assert_context_result(expected, reason)


@pytest.mark.parametrize(
    "wavelength, w_units, energy, e_units, tol",
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
def test_MonochromaticXrayWavelength_set_w(
    wavelength,
    w_units,
    energy,
    e_units,
    tol,
):
    flag: bool = False

    def request_solver_update(value: bool = True):
        """Mimic Core.request_solver_update() function."""
        nonlocal flag
        flag = value

    wl = MonochromaticXrayWavelength(
        2,
        units=w_units,
        wavelength_updated=request_solver_update,
    )
    wl.energy_units = e_units or DEFAULT_ENERGY_UNITS
    assert wl.wavelength_units == w_units or DEFAULT_WAVELENGTH_UNITS
    assert not flag

    wl.energy = energy
    assert math.isclose(wl.wavelength, wavelength, rel_tol=0.01)
    assert math.isclose(wl.energy, energy, abs_tol=tol), f"{wl.energy=!r}"
    assert flag


@pytest.mark.parametrize(
    "wavelength, w_units, energy, e_units, tol",
    [
        [1, None, 12.39842, "keV", 0.001],
        [1, "angstrom", 12.39842, None, 0.001],
        [1, "angstrom", 12.39842, "keV", 0.001],
        [100, "pm", 12.39842, "keV", 0.0001],
        [0.1, "nm", 12.39842, "keV", 0.001],
        [1, "angstrom", 12398.42, "eV", 0.001],
    ],
)
def test_MonochromaticXrayWavelength_change_units(
    wavelength,
    w_units,
    energy,
    e_units,
    tol,
):
    wl = MonochromaticXrayWavelength(1.0, units="angstrom")
    if e_units is not None:
        wl.energy_units = e_units
    if w_units is not None:
        wl.wavelength_units = w_units

    assert wl.energy_units == (e_units or "keV")
    assert wl.wavelength_units == (w_units or "angstrom")
    assert math.isclose(wl.wavelength, wavelength, rel_tol=tol)
    assert math.isclose(wl.energy, energy, rel_tol=tol)


@pytest.mark.parametrize(
    "factor, context, expected",
    [
        [2, does_not_raise(), None],
        [
            1 + DEFAULT_WAVELENGTH_DEADBAND / 2,
            pytest.raises(AssertionError),
            "test response",
        ],
        [
            1 + DEFAULT_WAVELENGTH_DEADBAND * 2,
            does_not_raise(),
            None,
        ],
    ],
)
def test_mono_wavelength_changed(factor, context, expected):
    from ..diffract import creator

    with context as reason:
        sim = creator(name="sim")
        assert not sim.core._solver_needs_update

        sim._source.energy *= factor
        assert sim.core._solver_needs_update, "test response"
    assert_context_result(expected, reason)
