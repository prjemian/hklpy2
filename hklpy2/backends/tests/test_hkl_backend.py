from .. import hkl_soleil


def test_version():
    assert "libhkl" in dir(hkl_soleil)
    assert isinstance(hkl_soleil.libhkl.VERSION, str)
    assert "HklSolver" in dir(hkl_soleil)

    solver = hkl_soleil.HklSolver()
    assert isinstance(solver.__version__, str)
    assert solver.__version__ == hkl_soleil.libhkl.VERSION
