"""Test the hklpy2.diffract module."""

import pytest

from ..diffract import DiffractometerBase


def test_simple():
    # TODO: Until more of the baae class is developed, an exception
    # will be raised if an object is created.  Test that situation.
    with pytest.raises(ValueError) as reason:
        DiffractometerBase("", name="dbase")
    assert "Must have at least 1 positioner and pseudo-positioner" in str(reason)
