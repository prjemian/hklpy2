import pytest

from .. import hkl_soleil


def test_version():
    assert "libhkl" in dir(hkl_soleil)
    libhkl = hkl_soleil.libhkl
    assert isinstance(libhkl.VERSION, str)
    assert "HklSolver" in dir(hkl_soleil)

    solver = hkl_soleil.HklSolver()
    assert isinstance(solver.__version__, str)
    assert solver.__version__ == libhkl.VERSION


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
    solver = hkl_soleil.HklSolver()
    assert solver is not None

    solver.setGeometry("E4CV")

    glist = solver.geometries
    assert len(glist) >= 18
    for gname in "E4CV E4CH E6C K4CV K6C ZAXIS TwoC".split():
        assert f"{gname}, hkl" in glist, f"{gname=}  {glist=}"
    # assert glist == [], f"{glist=}"
