import logging
from contextlib import nullcontext as does_not_raise

import pytest

from ..geom import creator
from ..operations.lattice import SI_LATTICE_PARAMETER
from ..user import add_sample
from ..user import get_diffractometer
from ..user import list_samples
from ..user import pa
from ..user import set_diffractometer
from ..user import set_lattice
from ..user import wh
from .common import TESTS_DIR
from .common import assert_context_result


@pytest.fixture(scope="function")
def fourc():
    fourc = creator(name="fourc")
    yield fourc


@pytest.mark.parametrize(
    "name, a, parms, lattice_str, context, expected",
    [
        [
            "sample",  # This sample already exists.
            2,
            {"gamma": 120},
            "Lattice(a=1, system='cubic')",  # Existing is not modified.
            does_not_raise(),  # Only warns via logger.
            None,
        ],
        [
            "NIST silicon standard",
            SI_LATTICE_PARAMETER,
            {},
            "Lattice(a=5.431, system='cubic')",
            does_not_raise(),
            None,
        ],
    ],
)
def test_add_sample(fourc, name, a, parms, lattice_str, context, expected):
    with context as reason:
        set_diffractometer(fourc)
        diffractometer = get_diffractometer()
        assert diffractometer == fourc
        assert list(diffractometer.samples) == ["sample"]

        add_sample(name, a, **parms)
        assert diffractometer.sample.name == name

        lattice = diffractometer.sample.lattice
        assert str(lattice) == lattice_str

    assert_context_result(expected, reason)


def test_add_sample_exists(fourc, caplog):
    set_diffractometer(fourc)
    diffractometer = get_diffractometer()
    assert diffractometer == fourc
    assert list(diffractometer.samples) == ["sample"]

    with caplog.at_level(logging.WARNING):
        add_sample("sample", 200, gamma=120)
    assert "already defined." in caplog.text
    assert "Add 'replace=True' to redefine" in caplog.text
    assert "Call 'set_lattice(a, ...)' to define" in caplog.text


def test_list_samples(fourc, capsys):
    fourc.restore(TESTS_DIR / "e4cv_orient.yml")
    set_diffractometer(fourc)

    list_samples()
    out, err = capsys.readouterr()
    assert len(out) > 0
    assert err == ""
    assert "> Sample(name='vibranium'," in out
    assert "\nSample(name='sample'," in out

    list_samples(full=True)
    out, err = capsys.readouterr()
    assert len(out) > 0
    assert err == ""
    assert "> {'name': 'vibranium'," in out
    assert "\n{'name': 'sample'," in out


def test_pa(fourc, capsys):
    set_diffractometer(fourc)
    assert get_diffractometer() == fourc

    tbl = pa()
    assert tbl is None
    out, err = capsys.readouterr()
    assert len(out) > 0
    assert err == ""
    out = [v.rstrip() for v in out.strip().splitlines()]
    expected = [
        "diffractometer='fourc'",
        "HklSolver(name='hkl_soleil', version='5.1.2', geometry='E4CV', engine_name='hkl', mode='bissector')",
        "Sample(name='sample', lattice=Lattice(a=1, system='cubic'))",
        "U=[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]",
        "UB=[[6.28318530718, -0.0, -0.0], [0.0, 6.28318530718, -0.0], [0.0, 0.0, 6.28318530718]]",
        "constraint: -180.0 <= omega <= 180.0",
        "constraint: -180.0 <= chi <= 180.0",
        "constraint: -180.0 <= phi <= 180.0",
        "constraint: -180.0 <= tth <= 180.0",
        "h=0, k=0, l=0",
        "wavelength=1.0",
        "omega=0, chi=0, phi=0, tth=0",
    ]
    assert len(out) == len(expected)
    assert out == expected


def test_select_diffractometer(fourc):
    set_diffractometer()
    assert get_diffractometer() is None

    set_diffractometer(fourc)
    assert get_diffractometer() == fourc


def test_set_lattice(fourc):
    set_diffractometer(fourc)
    diffractometer = get_diffractometer()
    assert diffractometer == fourc

    sample = diffractometer.sample
    assert str(sample.lattice) == "Lattice(a=1, system='cubic')"
    set_lattice(2, b=3, c=4)
    assert str(sample.lattice) == "Lattice(a=2, b=3, c=4, system='orthorhombic')"


def test_wh(fourc, capsys):
    set_diffractometer(fourc)
    assert get_diffractometer() == fourc

    tbl = wh()
    assert tbl is None
    out, err = capsys.readouterr()
    assert len(out) > 0
    assert err == ""
    out = [v.rstrip() for v in out.strip().splitlines()]
    expected = [
        "h=0, k=0, l=0",
        "wavelength=1.0",
        "omega=0, chi=0, phi=0, tth=0",
    ]
    assert len(out) == len(expected)
    assert out == expected
