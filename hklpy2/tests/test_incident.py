"""Test the incident beam module."""

import math
from contextlib import nullcontext as does_not_raise

import pint
import pytest
from ophyd.utils import ReadOnlyError

# from ..incident import DEFAULT_WAVELENGTH_DEADBAND
from ..incident import DEFAULT_ENERGY_UNITS
from ..incident import DEFAULT_SOURCE_TYPE
from ..incident import DEFAULT_WAVELENGTH
from ..incident import DEFAULT_WAVELENGTH_UNITS
from ..incident import EpicsMonochromatorRO
from ..incident import EpicsWavelengthRO
from ..incident import Wavelength
from ..incident import WavelengthXray
from ..incident import _WavelengthBase
from .common import assert_context_result

IOC_PREFIX = "hklpy2:"


def check_keys(wl, ref, tol=0.001):
    info = wl._asdict()
    for key, value in ref.items():
        assert key in info
        if isinstance(value, (float, int)):
            assert math.isclose(info[key], value, abs_tol=tol)
        else:
            assert info[key] == value


@pytest.mark.parametrize(
    "Klass, parms, ref, context, expected",
    [
        [
            _WavelengthBase,
            {},
            dict(
                wavelength=DEFAULT_WAVELENGTH,
                wavelength_units=DEFAULT_WAVELENGTH_UNITS,
                source_type=DEFAULT_SOURCE_TYPE,
            ),
            does_not_raise(),
            None,
        ],
        [
            _WavelengthBase,
            dict(wavelength=0.5),
            {},
            pytest.raises(ReadOnlyError),
            "The signal wl_wavelength is readonly.",
        ],
        [
            Wavelength,
            {},
            dict(
                wavelength=DEFAULT_WAVELENGTH,
                wavelength_units=DEFAULT_WAVELENGTH_UNITS,
                source_type=DEFAULT_SOURCE_TYPE,
            ),
            does_not_raise(),
            None,
        ],
        [
            Wavelength,
            dict(wavelength=2),
            dict(
                wavelength=2,
                wavelength_units=DEFAULT_WAVELENGTH_UNITS,
                source_type=DEFAULT_SOURCE_TYPE,
            ),
            does_not_raise(),
            None,
        ],
        [
            Wavelength,
            dict(wavelength_units="Mfurlongs"),
            dict(wavelength_units="Mfurlongs"),
            does_not_raise(),
            None,
        ],
        [
            Wavelength,
            dict(wavelength_units="banana"),
            {},
            pytest.raises(pint.UndefinedUnitError),
            "banana",
        ],
        [
            Wavelength,
            dict(source_type="unit testing"),
            dict(source_type="unit testing"),
            does_not_raise(),
            None,
        ],
        [
            WavelengthXray,
            {},
            dict(
                energy=12.3984,
                energy_units=DEFAULT_ENERGY_UNITS,
                wavelength=DEFAULT_WAVELENGTH,
                wavelength_units=DEFAULT_WAVELENGTH_UNITS,
                source_type=DEFAULT_SOURCE_TYPE,
            ),
            does_not_raise(),
            None,
        ],
        [
            WavelengthXray,
            dict(energy_units="banana"),
            {},
            pytest.raises(pint.UndefinedUnitError),
            "banana",
        ],
        [
            WavelengthXray,
            dict(energy_units="eV"),
            dict(energy_units="eV"),
            does_not_raise(),
            None,
        ],
        [WavelengthXray, dict(energy=10), dict(energy=10), does_not_raise(), None],
    ],
)
def test_constructors(Klass, parms, ref, context, expected):
    with context as reason:
        wl = Klass(**parms, name="wl")
        wl.wait_for_connection()
        check_keys(wl, ref)

    assert_context_result(expected, reason)


@pytest.mark.parametrize(
    "Klass, input, context, expected",
    [
        [Wavelength, {}, does_not_raise(), None],
        [
            Wavelength,
            {"wavelength": 2},  # missing "class='Wavelength'" key.
            pytest.raises(AssertionError),
            "isclose",
        ],
        [
            Wavelength,
            {"class": "Wavelength", "wavelength": 2},
            does_not_raise(),
            None,
        ],
        [
            Wavelength,
            {"class": "Wavelength", "wavelength_units": "kg"},  # incompatible
            pytest.raises(pint.DimensionalityError),
            DEFAULT_WAVELENGTH_UNITS,
        ],
        [
            Wavelength,
            {"class": "Wavelength", "wavelength_units": "banana"},
            pytest.raises(pint.UndefinedUnitError),
            "banana",
        ],
        [
            Wavelength,
            {"class": "Wavelength", "energy_units": "pg"},
            pytest.raises(pint.DimensionalityError),
            "kiloelectron_volt",
        ],
        [
            WavelengthXray,
            {"class": "WavelengthXray", "energy": 20},
            does_not_raise(),
            None,
        ],
        [
            WavelengthXray,
            {"class": "WavelengthXray", "energy_units": "eV"},
            does_not_raise(),
            None,
        ],
        [
            WavelengthXray,
            {"class": "WavelengthXray", "source_type": "unit testing"},
            pytest.raises(AssertionError),  # Can't change after constructor.
            DEFAULT_SOURCE_TYPE,
        ],
    ],
)
def test__fromdict(Klass, input, context, expected):
    with context as reason:
        wl = Klass(name="wl")
        wl.wait_for_connection()
        wl._fromdict(input)
        check_keys(wl, input)

    assert_context_result(expected, reason)


@pytest.mark.parametrize(
    "Klass, input, ref, context, expected",
    [
        [
            EpicsWavelengthRO,
            dict(prefix=IOC_PREFIX, pv_wavelength="wavelength"),
            {"class": "EpicsWavelengthRO", "wavelength": 1.0},
            does_not_raise(),
            None,
        ],
        [
            EpicsMonochromatorRO,
            dict(prefix=IOC_PREFIX, pv_energy="energy", pv_wavelength="wavelength"),
            {"class": "EpicsMonochromatorRO", "energy": 12.3984, "wavelength": 1.0},
            does_not_raise(),
            None,
        ],
        [
            EpicsWavelengthRO,
            dict(prefix=IOC_PREFIX, pv_wavelength="wrong_pv"),
            {},
            pytest.raises(TimeoutError),
            f"{IOC_PREFIX}wrong_pv",
        ],
    ],
)
def test_EpicsClasses(Klass, input, ref, context, expected):
    with context as reason:
        wl = Klass(name="wl", **input)
        wl.wait_for_connection(timeout=0.25)
        check_keys(wl, ref)

    assert_context_result(expected, reason)


@pytest.mark.parametrize(
    "Klass, parms, context, expected",
    [
        [
            WavelengthXray,
            {},
            does_not_raise(),
            None,
        ],
    ],
)
def test_wavelength_update(Klass, parms, context, expected):
    with context as reason:
        wl = Klass(**parms, name="wl")
        wl.wait_for_connection()
        # TODO: change the wavelength and test the update feature

    assert_context_result(expected, reason)
