from contextlib import nullcontext as does_not_raise

import pytest

from ..misc import load_yaml
from ..reflection import ConfigurationError
from ..reflection import Reflection
from ..reflection import ReflectionError
from ..reflection import ReflectionsDict

e4cv_r400_config_yaml = """
    name: r400
    geometry: E4CV
    pseudos:
        h: 4
        k: 0
        l: 0
    reals:
        omega: -145.451
        chi: 0
        phi: 0
        tth: 69.066
    wavelength: 1.54
    digits: 4
"""
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
            pytest.raises(ValueError),
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
            pytest.raises(ValueError),
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
            pytest.raises(ValueError),
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
            pytest.raises(ReflectionError),
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
            pytest.raises(ReflectionError),
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
    "parms, representation, probe, expected",
    [
        [[r100_parms], "(100)", does_not_raise(), None],
        [[r010_parms], "(010)", does_not_raise(), None],
        [[r100_parms, r010_parms], "(100)", does_not_raise(), None],
        [[r_1], "r1", does_not_raise(), None],
        [[r_2], "r2", does_not_raise(), None],
        [[r_1, r_4], "r4", does_not_raise(), None],
    ],
)
def test_ReflectionsDict(parms, representation, probe, expected):
    db = ReflectionsDict()
    assert len(db._asdict()) == 0

    with probe as reason:
        for i, refl in enumerate(parms, start=1):
            with pytest.raises(TypeError) as exc:
                db.add(refl)
            assert "Unexpected reflection=" in str(exc)

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

        assert representation in repr(db)

    if expected is None:
        assert reason is None
    else:
        assert expected in str(reason)


@pytest.mark.parametrize(
    "parms, probe, expect",
    [
        [[r100_parms], does_not_raise(), None],
        [[r010_parms], does_not_raise(), None],
        [[r100_parms, r010_parms], does_not_raise(), None],
        [[r_1], does_not_raise(), None],
        [[r_2], does_not_raise(), None],
        [[r_1, r_2], pytest.raises(ReflectionError), "matches one or more existing"],
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
            r = Reflection(*refl)
            assert r is not None
            db.add(r)
            assert len(db) == i
    if expect is not None:
        assert expect in str(reason), f"{reason=!r}"


def test_duplicate_reflection():
    db = ReflectionsDict()
    db.add(Reflection(*r_1))
    with pytest.raises(ReflectionError) as reason:
        db.add(Reflection(*r_1))
    assert "is known." in str(reason), f"{reason=!r}"

    with pytest.raises(ReflectionError) as reason:
        db.add(Reflection(*r_2))
    assert "matches one or more existing" in str(reason), f"{reason=!r}"


@pytest.mark.parametrize(
    "reflections, order, probe, expected",
    [
        [[r_1, r_4, r_5], ["r1", "r4"], does_not_raise(), None],
        [[r_1, r_4, r_5], ["r5", "r4"], does_not_raise(), None],
        [
            [r_1, r_4, r_5],
            ["r5"],
            pytest.raises(ReflectionError),
            "Need at least two reflections to swap.",
        ],
        [
            [r_1, r_4, r_5],
            [],
            pytest.raises(ReflectionError),
            "Need at least two reflections to swap.",
        ],
    ],
)
def test_swap(reflections, order, probe, expected):
    db = ReflectionsDict()
    original_order = []
    for params in reflections:
        ref = Reflection(*params)
        db.add(ref)
        original_order.append(ref.name)
    assert db.order == original_order

    with probe as reason:
        db.order = order
        assert db.order == order, f"{db.order=!r}"
        db.swap()
        assert db.order == list(reversed(order)), f"{db.order=!r}"

    if expected is None:
        assert reason is None
    else:
        assert expected in str(reason)


@pytest.mark.parametrize("config", [load_yaml(e4cv_r400_config_yaml)])
def test_fromdict(config):
    assert isinstance(config, dict), f"{config=!r}"
    assert "name" in config, f"{config=!r}"

    db = ReflectionsDict()
    assert len(db._asdict()) == 0

    refl = Reflection(
        config["name"],
        config["pseudos"],
        config["reals"],
        config["wavelength"],
        config["geometry"],
        list(config["pseudos"]),
        list(config["reals"]),
        digits=config["digits"],
    )
    assert refl is not None

    db._fromdict({config["name"]: config})
    assert len(db._asdict()) == 1
    assert config["name"] in db

    # check that we can restore same config
    with does_not_raise() as reason:
        refl._fromdict(config)
    assert reason is None

    # checks that mismatched Reflection configs raise
    temp_config = config.copy()
    temp_config["name"] = "mismatch will raise on refl._fromdict()"
    with pytest.raises(ConfigurationError) as reason:
        refl._fromdict(temp_config)
    assert "Mismatched name for reflection" in str(reason)

    temp_config = config.copy()
    temp_config["geometry"] = "mismatch will raise on refl._fromdict()"
    with pytest.raises(ConfigurationError) as reason:
        refl._fromdict(temp_config)
    assert "Mismatched geometry for reflection" in str(reason)

    temp_config = config.copy()
    temp_config["pseudos"] = {"aa": 1, "bb": "two"}
    with pytest.raises(ConfigurationError) as reason:
        refl._fromdict(temp_config)
    assert "Mismatched pseudo axis names for reflection" in str(reason)

    temp_config = config.copy()
    temp_config["reals"] = {"aa": 1, "bb": "two"}
    with pytest.raises(ConfigurationError) as reason:
        refl._fromdict(temp_config)
    assert "Mismatched real axis names for reflection" in str(reason)
