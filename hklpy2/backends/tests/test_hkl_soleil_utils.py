"""Test the hkl_soleil_utils module."""

from contextlib import nullcontext as does_not_raise

import pytest

from ...misc import SolverError
from ...tests.common import assert_context_result


@pytest.mark.parametrize(
    "system, library, version, context, expected",
    [
        [
            "Darwin",
            "Hkl",
            "5.0",
            pytest.raises(SolverError),
            "'hkl_soleil' only available for linux 64-bit",
        ],
        ["Linux", "Hkl", "5.0", does_not_raise(), None],
        [
            "Windows",
            "Hkl",
            "5.0",
            pytest.raises(SolverError),
            "'hkl_soleil' only available for linux 64-bit",
        ],
        [
            "Linux",
            "NOT FOUND",
            "5.0",
            pytest.raises(SolverError),
            "Cannot load 'gi' library:",
        ],
        [
            "Linux",
            "Hkl",
            "5.00",
            pytest.raises(SolverError),
            "Cannot load 'gi' library:",
        ],
    ],
)
def test_gi_require_library(system, library, version, context, expected):
    """Exercise the gi_require_library() function."""
    from ..hkl_soleil_utils import gi_require_library

    with context as reason:
        gi_require_library(system, library, version)
    assert_context_result(expected, reason)


def test_import_gi_failure():
    """Special case when 'gi' package is not installed."""
    import sys

    # Load the 'gi' package if possible.
    try:
        import gi  # noqa
    except (ImportError, ModuleNotFoundError):
        pass

    gi_module = sys.modules.get("gi")
    if gi_module is not None:
        # Remove it from the dictionary.
        del sys.modules["gi"]

    # Import the function after manipulating 'sys.modules'.
    from ..hkl_soleil_utils import gi_require_library

    # Proceed with testing, as above.
    expected = "Cannot import 'gi' (gobject-introspection) library."
    with pytest.raises(SolverError) as reason:
        gi_require_library("Linux", "Hkl", "5.0")
    assert_context_result(expected, reason)

    # Restore the 'gi' package to the dictionary.
    if gi_module is not None:
        sys.modules["gi"] = gi_module
