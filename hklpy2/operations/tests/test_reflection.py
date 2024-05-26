from contextlib import nullcontext as does_not_raise

import pytest

from ..reflection import Reflection
from ..reflection import ReflectionError
from ..reflection import ReflectionsDict

r100_parms = [
    "(100)",
    dict(h=1, k=0, l=0),
    dict(omega=10, chi=0, phi=0, tth=20),
    1.0,
    "E4CV",
    "h k l".split(),
    "omega chi phi tth".split(),
]
r010_parms = [
    "(010)",
    dict(h=0, k=1, l=0),
    dict(omega=10, chi=-90, phi=0, tth=20),
    1.0,
    "E4CV",
    "h k l".split(),
    "omega chi phi tth".split(),
]
# These are the same reflection (in content)
r_1 = ["r1", {"a": 1, "b": 2}, dict(c=1, d=2), 1, "abcd", ["a", "b"], ["c", "d"]]
r_2 = ["r2", {"a": 1, "b": 2}, dict(c=1, d=2), 1, "abcd", ["a", "b"], ["c", "d"]]
r_3 = ["r3", {"a": 1, "b": 2}, dict(c=1, d=2), 1, "abcd", ["a", "b"], ["c", "d"]]
# different ones
r_4 = ["r4", {"a": 1, "b": 3}, dict(c=1, d=2), 1, "abcd", ["a", "b"], ["c", "d"]]
r_5 = ["r5", {"a": 1, "b": 4}, dict(c=1, d=2), 1, "abcd", ["a", "b"], ["c", "d"]]


@pytest.mark.parametrize(
    "name, pseudos, reals, wavelength, geometry, pseudo_axis_names, real_axis_names, probe, expect",
    [
        r100_parms + [does_not_raise(), None],  # good case
        r010_parms + [does_not_raise(), None],  # good case
        [
            1,  # wrong type
            dict(h=1, k=0, l=0),
            dict(omega=10, chi=0, phi=0, tth=20),
            1.0,
            "E4CV",
            "h k l".split(),
            "omega chi phi tth".split(),
            pytest.raises(TypeError),
            "Must supply str",
        ],
        [
            None,  # wrong type
            dict(h=1, k=0, l=0),
            dict(omega=10, chi=0, phi=0, tth=20),
            1.0,
            "E4CV",
            "h k l".split(),
            "omega chi phi tth".split(),
            pytest.raises(TypeError),
            "Must supply str",
        ],
        [
            "one",
            [1, 0, 0],  # wrong type
            dict(omega=10, chi=0, phi=0, tth=20),
            1.0,
            "E4CV",
            "h k l".split(),
            "omega chi phi tth".split(),
            pytest.raises(TypeError),
            "Must supply dict",
        ],
        [
            "one",
            dict(hh=1, kk=0, ll=0),  # wrong keys
            dict(omega=10, chi=0, phi=0, tth=20),
            1.0,
            "E4CV",
            "h k l".split(),
            "omega chi phi tth".split(),
            pytest.raises(KeyError),
            "pseudo axis 'hh' unknown",
        ],
        [
            "one",
            dict(h=1, k=0, l=0, m=0),  # extra key
            dict(omega=10, chi=0, phi=0, tth=20),
            1.0,
            "E4CV",
            "h k l".split(),
            "omega chi phi tth".split(),
            pytest.raises(KeyError),
            "pseudo axis 'm' unknown",
        ],
        [
            "one",
            dict(h=1, k=0, l=0),
            [10, 0, 0, 20],  # wrong type
            1.0,
            "E4CV",
            "h k l".split(),
            "omega chi phi tth".split(),
            pytest.raises(TypeError),
            "Must supply dict,",
        ],
        [
            "one",
            dict(h=1, k=0, l=0),
            dict(theta=10, chi=0, phi=0, tth=20),  # wrong key
            1.0,
            "E4CV",
            "h k l".split(),
            "omega chi phi tth".split(),
            pytest.raises(KeyError),
            "real axis 'theta' unknown",
        ],
        [
            "one",
            dict(h=1, k=0, l=0),
            dict(omega=10, chi=0, phi=0, tth=20),
            "1.0",  # wrong type
            "E4CV",
            "h k l".split(),
            "omega chi phi tth".split(),
            pytest.raises(TypeError),
            "Must supply number,",
        ],
        [
            "one",
            dict(h=1, k=0, l=0),
            dict(omega=10, chi=0, phi=0, tth=20),
            None,  # wrong type
            "E4CV",
            "h k l".split(),
            "omega chi phi tth".split(),
            pytest.raises(TypeError),
            "Must supply number,",
        ],
        [
            "one",
            dict(h=1, k=0, l=0),
            dict(omega=10, chi=0, phi=0, tth=20),
            -1,  # not allowed
            "E4CV",
            "h k l".split(),
            "omega chi phi tth".split(),
            pytest.raises(ValueError),
            "Must be >=0,",
        ],
        [
            "one",
            dict(h=1, k=0, l=0),
            dict(omega=10, chi=0, phi=0, tth=20),
            0,  # not allowed: will cause DivideByZero later
            "E4CV",
            "h k l".split(),
            "omega chi phi tth".split(),
            pytest.raises(ValueError),
            "Must be >=0,",
        ],
        [
            "one",
            dict(h=1, k=0, l=0),
            dict(omega=10, chi=0, phi=0, tth=20),
            1,
            None,  # allowed
            "h k l".split(),
            "omega chi phi tth".split(),
            does_not_raise(),
            None,
        ],
        [
            "one",
            dict(a=1, b=2),
            dict(c=10, d=0, e=20),
            1,
            "test",  # allowed
            "a b".split(),
            "c d e".split(),
            does_not_raise(),
            None,
        ],
        [
            "one",
            dict(h=1, l=0),  # missing pseudo
            dict(omega=10, chi=0, phi=0, tth=20),
            1.0,
            "E4CV",
            "h k l".split(),
            "omega chi phi tth".split(),
            pytest.raises(KeyError),
            "Missing pseudo axis",
        ],
        [
            "one",
            dict(h=1, k=0, l=0),
            dict(omega=10, chi=0, tth=20),  # missing real
            1.0,
            "E4CV",
            "h k l".split(),
            "omega chi phi tth".split(),
            pytest.raises(KeyError),
            "Missing real axis",
        ],
    ],
)
def test_Reflection(
    name,
    pseudos,
    reals,
    wavelength,
    geometry,
    pseudo_axis_names,
    real_axis_names,
    probe,
    expect,
):
    with probe as reason:
        refl = Reflection(
            name,
            pseudos,
            reals,
            wavelength,
            geometry,
            pseudo_axis_names,
            real_axis_names,
        )
    if expect is not None:
        assert expect in str(reason), f"{reason}"
    else:
        refl_dict = refl._asdict()
        for k in "name pseudos reals wavelength geometry".split():
            assert k in refl_dict, f"{k=}"

        rep = repr(refl)
        assert rep.startswith("Reflection(")
        assert f"{name=!r}" in rep, f"{rep}"
        assert f"{pseudos=!r}" in rep, f"{rep}"
        assert f"{reals=!r}" in rep, f"{rep}"
        assert f"{wavelength=!r}" in rep, f"{rep}"
        assert f"{geometry=!r}" in rep, f"{rep}"
        assert rep.endswith(")")


@pytest.mark.parametrize(
    "parms",
    [
        [r100_parms],
        [r010_parms],
        [r100_parms, r010_parms],
        [r_1],
        [r_2],
        [r_1, r_4],
    ],
)
def test_ReflectionsDict(parms):
    db = ReflectionsDict()
    assert len(db._asdict()) == 0

    for i, refl in enumerate(parms, start=1):
        with pytest.raises(TypeError) as reason:
            db.add(refl)
        assert "Unexpected reflection=" in str(reason)

        db.add(Reflection(*refl))
        assert len(db._asdict()) == i
        assert len(db.order) == i

        r1 = list(db.values())[0]
        db.setor([r1])
        assert len(db._asdict()) == i  # unchanged
        assert len(db.order) == 1

        db.set_orientation_reflections([r1])
        assert len(db._asdict()) == i  # unchanged
        assert len(db.order) == 1

        db.order = [r1.name]
        assert len(db._asdict()) == i  # unchanged
        assert len(db.order) == 1


@pytest.mark.parametrize(
    "parms, probe, expect",
    [
        [[r100_parms], does_not_raise(), None],
        [[r010_parms], does_not_raise(), None],
        [[r100_parms, r010_parms], does_not_raise(), None],
        [[r_1], does_not_raise(), None],
        [[r_2], does_not_raise(), None],
        [[r_1, r_2], pytest.raises(ReflectionError), "matches existing"],
        [[r_1, r_4], does_not_raise(), None],
        [
            [r100_parms, r010_parms, r_1, r_4],
            pytest.raises(ValueError),
            "geometry does not match previous reflections",
        ],
        [
            [r100_parms, r_2],
            pytest.raises(ValueError),
            "geometry does not match previous reflections",
        ],
    ],
)
def test_IncompatibleReflectionsDict(parms, probe, expect):
    db = ReflectionsDict()
    assert len(db._asdict()) == 0

    with probe as reason:
        for i, refl in enumerate(parms, start=1):
            db.add(Reflection(*refl))
    if expect is not None:
        assert expect in str(reason), f"{reason=!r}"


def test_duplicate_reflection():
    db = ReflectionsDict()
    db.add(Reflection(*r_1))
    with pytest.raises(ReflectionError) as reason:
        db.add(Reflection(*r_1))
    assert "already defined." in str(reason), f"{reason=!r}"

    with pytest.raises(ReflectionError) as reason:
        db.add(Reflection(*r_2))
    assert "matches existing" in str(reason), f"{reason=!r}"


def test_swap():
    db = ReflectionsDict()
    db.add(Reflection(*r_1))
    db.add(Reflection(*r_4))
    db.add(Reflection(*r_5))
    assert db.order == "r1 r4 r5".split()

    db.order = ["r1", "r4"]
    assert db.order == "r1 r4".split(), f"{db.order=!r}"
    db.swap()
    assert db.order == "r4 r1".split(), f"{db.order=!r}"

    db.order = "r5", "r4"  # repeat as tuple
    assert db.order == "r5 r4".split(), f"{db.order=!r}"
    db.swap()
    assert db.order == "r4 r5".split(), f"{db.order=!r}"
