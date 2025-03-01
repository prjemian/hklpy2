import logging
from collections import namedtuple
from contextlib import nullcontext as does_not_raise

import numpy.testing
import pyRestTable
import pytest

from ..geom import creator
from ..operations.lattice import SI_LATTICE_PARAMETER
from ..operations.misc import ReflectionError
from ..user import add_sample
from ..user import cahkl
from ..user import cahkl_table
from ..user import calc_UB
from ..user import get_diffractometer
from ..user import list_samples
from ..user import or_swap
from ..user import pa
from ..user import set_diffractometer
from ..user import set_energy
from ..user import set_lattice
from ..user import setor
from ..user import wh
from ..wavelength_support import ConstantMonochromaticWavelength
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


def test_cahkl(fourc):
    fourc.operator.constraints["tth"].limits = (0, 180)
    for axis in fourc.real_positioners:
        # Start at zero, make certain cahkl() will not move the motors!
        axis.move(0)

    set_diffractometer(fourc)

    for axis in fourc.real_positioners:
        # Verify cahkl() did not move the motors!
        numpy.testing.assert_approx_equal(axis.position, 0)

    # use the default "main" sample and UB matrix
    for position, expected in zip(cahkl(1, 0, 0), (30, 0, 90, 60)):
        assert round(position) == expected


def test_cahkl_table(fourc):
    fourc.operator.constraints["tth"].limits = (0, 180)
    set_diffractometer(fourc)

    # use the default "main" sample and UB matrix
    HklTuple = namedtuple("HklTuple", "h k l".split())
    rlist = [HklTuple(1, 0, 0), HklTuple(0, 1, 0)]
    table = cahkl_table(*rlist, digits=0)
    assert isinstance(table, pyRestTable.Table)

    expected = """
    ========= ======== ===== === === ===
    (hkl)     solution omega chi phi tth
    ========= ======== ===== === === ===
    (1, 0, 0) 0        30    0   90  60
    (0, 1, 0) 0        30    90  0   60
    ========= ======== ===== === === ===
    """.strip().splitlines()
    for el, rl in list(zip(expected[3:5], str(table).strip().splitlines()[3:5])):
        # just compare the position values
        for e, r in list(zip(el.split()[-4:], rl.split()[-4:])):
            assert float(r) == float(e)


def test_calc_UB(fourc):
    fourc.omega.move(-145.451)
    fourc.chi.move(90)
    fourc.phi.move(0)
    fourc.tth.move(69.0966)
    set_diffractometer(fourc)
    add_sample("silicon standard", SI_LATTICE_PARAMETER)
    r1 = setor(4, 0, 0, tth=69.0966, omega=-145.451, chi=0, phi=0, wavelength=1.54)
    r2 = setor(0, 4, 0)

    ub = calc_UB(r1, r2)
    assert isinstance(ub, (list, numpy.ndarray))


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


@pytest.mark.parametrize(
    "file, sample, nrefs, or_refs, context, expected",
    [
        [
            TESTS_DIR / "e4cv_orient.yml",
            "vibranium",
            3,
            "r040 r004".split(),
            does_not_raise(),
            None,
        ],
        [
            TESTS_DIR / "e4cv_orient.yml",
            "sample",
            0,
            [],
            pytest.raises(ReflectionError),
            "Need at least two reflections to swap.",
        ],
    ],
)
def test_or_swap(fourc, file, sample, nrefs, or_refs, context, expected):
    with context as reason:
        fourc.restore(file)
        set_diffractometer(fourc)
        diffractometer = get_diffractometer()
        diffractometer.sample = sample
        assert diffractometer.sample.name == sample
        assert len(diffractometer.sample.reflections) == nrefs
        assert len(or_refs) in (0, 2)
        assert diffractometer.sample.reflections.order == or_refs
        UB0 = diffractometer.sample.UB

        UB = or_swap()
        assert diffractometer.sample.reflections.order == list(reversed(or_refs))
        assert UB != UB0

        UB = or_swap()
        assert diffractometer.sample.reflections.order == or_refs
        assert UB != UB0

    assert_context_result(expected, reason)


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


def test_set_diffractometer(fourc):
    set_diffractometer()
    assert get_diffractometer() is None

    set_diffractometer(fourc)
    assert get_diffractometer() == fourc

    with pytest.raises(TypeError) as reason:
        set_diffractometer(object())
    expected = "must be an hklpy2 'DiffractometerBase' subclass"
    assert_context_result(expected, reason)


def test_set_lattice(fourc):
    set_diffractometer(fourc)
    diffractometer = get_diffractometer()
    assert diffractometer == fourc

    sample = diffractometer.sample
    assert str(sample.lattice) == "Lattice(a=1, system='cubic')"
    set_lattice(2, b=3, c=4)
    assert str(sample.lattice) == "Lattice(a=2, b=3, c=4, system='orthorhombic')"


@pytest.mark.parametrize(
    "energy, units, offset, context, expected",
    [
        [8, "keV", 0, does_not_raise(), None],
        [8.1, "keV", -0.03, does_not_raise(), None],
        [7500, "eV", 0, does_not_raise(), None],
        [7100, "eV", 25, does_not_raise(), None],
    ],
)
def test_set_energy(fourc, energy, units, offset, context, expected):
    with context as reason:
        set_diffractometer(fourc)
        source = get_diffractometer()._source

        set_energy(energy, units=units, offset=None)  # TODO: #35
        # numpy.testing.assert_approx_equal(source.energy_offset, 0)
        assert source.energy_units == units
        numpy.testing.assert_approx_equal(source.energy, energy)
    assert_context_result(expected, reason)

    if offset != 0:  # TODO: #35
        with pytest.raises(NotImplementedError) as reason:
            set_energy(energy, units=units, offset=offset)
        expected = "energy offset not implemented"
        assert_context_result(expected, reason)

    # Edge case
    wavelength = source.wavelength
    get_diffractometer()._source = ConstantMonochromaticWavelength(wavelength)
    with pytest.raises(TypeError) as reason:
        set_energy(energy)
    expected = "'set_energy()' not supported "
    assert_context_result(expected, reason)


def test_setor(fourc):
    set_diffractometer(fourc)
    add_sample("silicon standard", SI_LATTICE_PARAMETER)
    diffractometer = get_diffractometer()

    assert len(diffractometer.sample.reflections) == 0
    r400 = setor(4, 0, 0, -145.451, 0, 0, 69.0966, wavelength=1.54)
    assert len(diffractometer.sample.reflections) == 1
    assert list(diffractometer.sample.reflections) == [r400.name]

    diffractometer.omega.move(-145.451)
    diffractometer.chi.move(90)
    diffractometer.phi.move(0)
    diffractometer.tth.move(69.0966)
    r040 = setor(0, 4, 0)
    assert len(diffractometer.sample.reflections) == 2
    assert list(diffractometer.sample.reflections) == [r400.name, r040.name]

    r004 = setor(
        0,
        0,
        4,
        chi=90,
        omega=-145.451,
        phi=0,
        tth=69.0966,
        name="r004",
    )
    assert len(diffractometer.sample.reflections) == 3
    assert list(diffractometer.sample.reflections) == [r400.name, r040.name, r004.name]


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
