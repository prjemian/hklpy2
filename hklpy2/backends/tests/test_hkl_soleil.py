import math

import pytest

from .. import hkl_soleil


def test_version():
    assert "libhkl" in dir(hkl_soleil)
    libhkl = hkl_soleil.libhkl
    assert isinstance(libhkl.VERSION, str)
    assert "HklSolver" in dir(hkl_soleil)

    solver = hkl_soleil.HklSolver("E4CV")
    assert isinstance(solver.version, str)
    assert solver.version == libhkl.VERSION


@pytest.mark.parametrize(
    "gname, ename, reals",
    [
        ["E4CV", "hkl", ["omega", "chi", "phi", "tth"]],
        ["E4CH", "hkl", ["omega", "chi", "phi", "tth"]],
        ["E6C", "hkl", ["mu", "omega", "chi", "phi", "gamma", "delta"]],
        ["K4CV", "hkl", ["komega", "kappa", "kphi", "tth"]],
        ["K6C", "hkl", ["mu", "komega", "kappa", "kphi", "gamma", "delta"]],
        ["PETRA3 P09 EH2", "hkl", ["mu", "omega", "chi", "phi", "delta", "gamma"]],
        ["PETRA3 P23 4C", "hkl", ["omega_t", "mu", "gamma", "delta"]],
        [
            "PETRA3 P23 6C",
            "hkl",
            ["omega_t", "mu", "omega", "chi", "phi", "gamma", "delta"],
        ],
        ["ZAXIS", "hkl", ["mu", "omega", "delta", "gamma"]],
    ],
)
def test_engine(gname, ename, reals):
    libhkl = hkl_soleil.libhkl
    assert libhkl is not None

    factories = libhkl.factories()
    assert len(factories) > 1
    assert gname in factories

    factory = factories[gname]
    assert factory is not None

    geometry = factory.create_new_geometry()
    assert geometry.name_get() == gname

    r_axes = geometry.axis_names_get()
    assert r_axes == reals, f"{r_axes=}"

    # tip: libhkl will dump core if engines is combined into following:
    #   factory.create_new_engine_list().engine_get_by_name(ename)
    engines = factory.create_new_engine_list()
    assert engines is not None

    engine = engines.engine_get_by_name(ename)
    assert engine is not None
    assert engine.name_get() == ename

    p_axes = engine.pseudo_axis_names_get()
    assert p_axes == "h k l".split(), f"{p_axes=}"


def test_geometries():
    solver = hkl_soleil.HklSolver("E4CV")  # to get the geometries
    assert solver is not None

    glist = solver.geometries()
    assert len(glist) >= 18
    for gname in "E4CV E4CH E6C K4CV K6C ZAXIS".split():
        assert gname in glist, f"{gname=}  {glist=}"


def test_affine():
    """Test the lattice parameter refinement."""
    from ... import SI_LATTICE_PARAMETER
    from ... import SimulatedE4CV
    from ...operations.lattice import SI_LATTICE_PARAMETER_UNCERTAINTY

    e4cv = SimulatedE4CV("", name="e4cv")
    assert e4cv is not None

    e4cv.add_sample("silicon", SI_LATTICE_PARAMETER)
    e4cv.add_reflection(
        (4, 0, 0),
        dict(tth=69.1, omega=-145.5, chi=0, phi=0),
        wavelength=1.54,
        name="r1",
    )
    e4cv.add_reflection(
        (0, 4, 0),
        dict(tth=69.1, omega=-145.5, chi=90, phi=0),
        wavelength=1.54,
        name="r2",
    )
    e4cv.add_reflection(
        (0, 0, 4),
        dict(tth=69.1, omega=-145.5, chi=0, phi=90),
        wavelength=1.54,
        name="r3",
    )
    assert len(e4cv.sample.reflections) == 3

    # as-defined, sample is cubic with precise lattice parameter
    tol = SI_LATTICE_PARAMETER_UNCERTAINTY
    assert math.isclose(e4cv.sample.lattice.a, SI_LATTICE_PARAMETER, abs_tol=tol)
    assert math.isclose(e4cv.sample.lattice.b, SI_LATTICE_PARAMETER, abs_tol=tol)
    assert math.isclose(e4cv.sample.lattice.c, SI_LATTICE_PARAMETER, abs_tol=tol)
    assert math.isclose(e4cv.sample.lattice.alpha, 90, abs_tol=tol)
    assert math.isclose(e4cv.sample.lattice.beta, 90, abs_tol=tol)
    assert math.isclose(e4cv.sample.lattice.gamma, 90, abs_tol=tol)

    e4cv.operator.refine_lattice()

    # refined lattice parameter is not so precise
    assert not math.isclose(e4cv.sample.lattice.a, SI_LATTICE_PARAMETER, abs_tol=tol)
    assert not math.isclose(e4cv.sample.lattice.b, SI_LATTICE_PARAMETER, abs_tol=tol)
    assert not math.isclose(e4cv.sample.lattice.c, SI_LATTICE_PARAMETER, abs_tol=tol)
    assert not math.isclose(e4cv.sample.lattice.alpha, 90, abs_tol=tol)
    assert not math.isclose(e4cv.sample.lattice.beta, 90, abs_tol=tol)
    assert not math.isclose(e4cv.sample.lattice.gamma, 90, abs_tol=tol)

    # relax the precision quite a bit
    tol = 0.001
    assert math.isclose(e4cv.sample.lattice.a, SI_LATTICE_PARAMETER, rel_tol=tol)
    assert math.isclose(e4cv.sample.lattice.b, SI_LATTICE_PARAMETER, rel_tol=tol)
    assert math.isclose(e4cv.sample.lattice.c, SI_LATTICE_PARAMETER, rel_tol=tol)
    assert math.isclose(e4cv.sample.lattice.alpha, 90, rel_tol=tol)
    assert math.isclose(e4cv.sample.lattice.beta, 90, rel_tol=tol)
    assert math.isclose(e4cv.sample.lattice.gamma, 90, rel_tol=tol)
