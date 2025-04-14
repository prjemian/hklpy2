"""Test the package constructor."""

from unittest.mock import Mock

import hklpy2


def test_get_version():
    version = "111.111.111"
    hklpy2._get_version = Mock(return_value=version)
    assert hklpy2._get_version() == version
