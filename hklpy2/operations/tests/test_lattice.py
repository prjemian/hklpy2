from contextlib import nullcontext as does_not_raise

import pytest

from ..lattice import Lattice
from ..lattice import LatticeError
from ..misc import load_yaml


@pytest.mark.parametrize(
    "system, a, others, context, reason",
    [
        ["cubic", 5, dict(), does_not_raise(), None],
        ["hexagonal", 4, dict(c=3, gamma=120), does_not_raise(), None],
        ["rhombohedral", 4, dict(alpha=80.2), does_not_raise(), None],
        ["rhombohedral", 4, dict(alpha=120), does_not_raise(), None],
        ["tetragonal", 4, dict(c=3), does_not_raise(), None],
        ["orthorhombic", 4, dict(b=5, c=3), does_not_raise(), None],
        ["monoclinic", 4, dict(b=5, c=3, beta=75), does_not_raise(), None],
        [
            "triclinic",
            4,
            dict(b=5, c=3, alpha=75, beta=85, gamma=95),
            does_not_raise(),
            None,
        ],
        [
            "hexagonal",
            4,
            dict(gamma=120),  # hexagonal needs a != c
            pytest.raises(LatticeError),
            "Unrecognized crystal system:",
        ],
    ],
)
def test_repr(system, a, others, context, reason):
    lattice = Lattice(a, **others)
    assert lattice is not None

    with context as info:
        rep = repr(lattice)
        assert rep.startswith("Lattice(")
        assert "a=" in rep
        assert "system=" in rep
        assert repr(system) in rep, f"{system=!r} lattice={rep!r}"
        assert rep.endswith(")")
    if reason is not None:
        assert reason in str(info.value)


@pytest.mark.parametrize(
    "args, kwargs, expected",
    [
        [[5], {}, (5, 5, 5, 90, 90, 90)],  # cubic
        [[4], dict(c=3.0, gamma=120), (4, 4, 3, 90, 90, 120)],  # hexagonal
        [[4], dict(alpha=80.1), (4, 4, 4, 80.1, 80.1, 80.1)],  # rhombohedral
        [[4], dict(c=3), (4, 4, 3, 90, 90, 90)],  # tetragonal
        [[4, 5, 3], {}, (4, 5, 3, 90, 90, 90)],  # orthorhombic
        [[4, 5, 3], dict(beta=75), (4, 5, 3, 90, 75, 90)],  # monoclinic
        [[4, 5, 3, 75, 85, 95], {}, (4, 5, 3, 75, 85, 95)],  # triclinic
    ],
)
def test_crystal_classes(args, kwargs, expected):
    """
    Test each of the 7 crystal lattice types for correct lattices.
    """
    assert isinstance(expected, (list, tuple))
    latt = Lattice(*args, **kwargs)
    assert isinstance(latt, Lattice)
    assert list(latt._asdict().values()) == list(expected), f"{latt=}"


def test_equal():
    l1 = Lattice(4.000_1)
    l2 = Lattice(4.000_0)
    l1.digits = 3
    assert l1 == l2

    l1.digits = 4
    assert l1 != l2


def test_fromdict():
    text = """
      a: 3
      b: 4
      c: 5
      alpha: 75.0
      beta: 85.0
      gamma: 91.0
    """
    config = load_yaml(text)
    assert isinstance(config, dict), f"{config=!r}"
    for k in "a b c alpha beta gamma".split():
        assert k in config, f"{k=!r}  {config=!r}"

    lattice = Lattice(1)
    for k in "a b c alpha beta gamma".split():
        assert getattr(lattice, k) != config[k], f"{k=!r}  {lattice=!r}"

    lattice._fromdict(config)
    for k in "a b c alpha beta gamma".split():
        assert getattr(lattice, k) == config[k], f"{k=!r}  {lattice=!r}"
