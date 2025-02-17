"""
Test code from geom module.

Mostly, this tests code not already tested elsewhere.
"""

import pytest
from ophyd import EpicsMotor
from ophyd import SoftPositioner

from ..geom import diffractometer_factory


@pytest.mark.parametrize(
    "reals, positioner_class",
    [
        [dict(omega="zgp:m1", chi="zgp:m2", phi="zgp:m3", tth="zgp:m4"), EpicsMotor],
        [dict(aaa=None, bbb=None, ccc=None, ddd=None), SoftPositioner],
        [{}, SoftPositioner],
    ],
)
def test_diffractometer_factory_reals(reals, positioner_class):
    diffractometer = diffractometer_factory(name="diffractometer", reals=reals)
    assert diffractometer is not None
    for axis in diffractometer.real_axis_names:
        if len(reals) > 0:
            assert axis in reals
        assert isinstance(getattr(diffractometer, axis), positioner_class)
