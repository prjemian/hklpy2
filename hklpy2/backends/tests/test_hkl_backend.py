from .. import hkl_backend


def test_version():
    assert "libhkl" in dir(hkl_backend)
    assert isinstance(hkl_backend.libhkl.VERSION, str)
    assert "HklSolver" in dir(hkl_backend)

    solver = hkl_backend.HklSolver()
    assert isinstance(solver.__version__, str)
    assert solver.__version__ == hkl_backend.libhkl.VERSION
