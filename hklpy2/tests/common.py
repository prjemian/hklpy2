"""Code that is common to several tests."""

import pathlib

HKLPY2_DIR = pathlib.Path(__file__).parent.parent
TESTS_DIR = HKLPY2_DIR / "tests"
PV_ENERGY = "hklpy2:energy"
PV_WAVELENGTH = "hklpy2:wavelength"


def assert_context_result(expected, reason):
    """Common handling for tests below."""
    if expected is None:
        assert reason is None
    else:
        assert expected in str(reason), f"{expected=!r} {reason=}"
