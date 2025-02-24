"""
Test code from geom module.

Mostly, this tests code not already tested elsewhere.
"""

import pathlib
from contextlib import nullcontext as does_not_raise

import pytest
from ophyd import EpicsMotor
from ophyd import SoftPositioner

from ..geom import creator
from .common import assert_context_result

HKLPY2_DIR = pathlib.Path(__file__).parent.parent


@pytest.mark.parametrize(
    "config_file",
    ["e4cv_orient.yml", "fourc-configuration.yml"],
)
@pytest.mark.parametrize(
    "pseudos, reals, positioner_class, context, expected",
    [
        [
            [],
            dict(omega="IOC:m1", chi="IOC:m2", phi="IOC:m3", tth="IOC:m4"),
            EpicsMotor,
            does_not_raise(),
            None,
        ],
        [
            [],
            dict(aaa=None, bbb=None, ccc=None),
            SoftPositioner,
            pytest.raises(KeyError),
            "reals, received ",
        ],
        [
            [],
            dict(aaa=None, bbb=None, ccc=None, ddd=None),
            SoftPositioner,
            does_not_raise(),
            None,
        ],
        [
            [],
            dict(aaa=None, bbb=None, ccc=None, ddd=None, eee=None),
            SoftPositioner,
            does_not_raise(),
            None,
        ],
        [
            [],
            dict(aaa="IOC:m1", bbb=None, ccc=None, ddd=None, eee=None),
            (EpicsMotor, SoftPositioner),
            does_not_raise(),
            None,
        ],
        [[], {}, SoftPositioner, does_not_raise(), None],
        [
            "h k".split(),
            {},
            SoftPositioner,
            does_not_raise(),
            None,
        ],
        [
            "h2 k2 l2 psi alpha beta".split(),
            {},
            SoftPositioner,
            does_not_raise(),
            None,
        ],
    ],
)
def test_creator_reals(
    pseudos, reals, positioner_class, context, expected, config_file
):
    with context as reason:
        diffractometer = creator(name="diffractometer", pseudos=pseudos, reals=reals)
        assert diffractometer is not None
        for axis in diffractometer.real_axis_names:
            if len(reals) > 0:
                assert axis in reals
            assert isinstance(getattr(diffractometer, axis), positioner_class)
        diffractometer.restore(HKLPY2_DIR / "tests" / config_file)

    assert_context_result(expected, reason)
