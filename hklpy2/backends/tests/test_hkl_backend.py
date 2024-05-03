from .. import hkl_backend as backend


def test_simple():
    assert "libhkl" in dir(backend)
    assert isinstance(backend.libhkl.VERSION, str)
