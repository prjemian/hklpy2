"""
diffractometers
"""

from ophyd import Component as Cpt
from ophyd import Kind
from ophyd import PseudoSingle
from ophyd import SoftPositioner

from ..diffract import DiffractometerBase

HN = Kind.hinted | Kind.normal


class Fourc(DiffractometerBase):
    """Test case."""

    h = Cpt(PseudoSingle, "", kind=HN)  # noqa: E741
    k = Cpt(PseudoSingle, "", kind=HN)  # noqa: E741
    l = Cpt(PseudoSingle, "", kind=HN)  # noqa: E741

    theta = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=HN)
    chi = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=HN)
    phi = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=HN)
    ttheta = Cpt(SoftPositioner, limits=(-170, 170), init_pos=0, kind=HN)

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            solver="hkl_soleil",
            geometry="E4CV",
            solver_kwargs={"engine": "hkl"},
            **kwargs,
        )


class AugmentedFourc(Fourc):
    """Test case."""

    # define a few more axes,
    # extra parameters for some geometries/engines/modes

    h2 = Cpt(PseudoSingle, "", kind=HN)  # noqa: E741
    k2 = Cpt(PseudoSingle, "", kind=HN)  # noqa: E741
    l2 = Cpt(PseudoSingle, "", kind=HN)  # noqa: E741
    psi = Cpt(SoftPositioner, limits=(-170, 170), init_pos=0, kind=HN)

    # and a few more axes not used by 4-circle code

    q = Cpt(PseudoSingle, "", kind=HN)  # noqa: E741
    mu = Cpt(SoftPositioner, limits=(-170, 170), init_pos=0, kind=HN)
    nu = Cpt(SoftPositioner, limits=(-170, 170), init_pos=0, kind=HN)
    omicron = Cpt(SoftPositioner, limits=(-170, 170), init_pos=0, kind=HN)


class MultiAxis99(DiffractometerBase):
    """Test case.  9 pseudo axes and 9 real axes."""

    p1 = Cpt(PseudoSingle, "", kind=HN)  # noqa: E741
    p2 = Cpt(PseudoSingle, "", kind=HN)  # noqa: E741
    p3 = Cpt(PseudoSingle, "", kind=HN)  # noqa: E741
    p4 = Cpt(PseudoSingle, "", kind=HN)  # noqa: E741
    p5 = Cpt(PseudoSingle, "", kind=HN)  # noqa: E741
    p6 = Cpt(PseudoSingle, "", kind=HN)  # noqa: E741
    p7 = Cpt(PseudoSingle, "", kind=HN)  # noqa: E741
    p8 = Cpt(PseudoSingle, "", kind=HN)  # noqa: E741
    p9 = Cpt(PseudoSingle, "", kind=HN)  # noqa: E741

    r1 = Cpt(SoftPositioner, init_pos=0, kind=HN)
    r2 = Cpt(SoftPositioner, init_pos=0, kind=HN)
    r3 = Cpt(SoftPositioner, init_pos=0, kind=HN)
    r4 = Cpt(SoftPositioner, init_pos=0, kind=HN)
    r5 = Cpt(SoftPositioner, init_pos=0, kind=HN)
    r6 = Cpt(SoftPositioner, init_pos=0, kind=HN)
    r7 = Cpt(SoftPositioner, init_pos=0, kind=HN)
    r8 = Cpt(SoftPositioner, init_pos=0, kind=HN)
    r9 = Cpt(SoftPositioner, init_pos=0, kind=HN)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class NoOpTh2Th(DiffractometerBase):
    """Test case."""

    q = Cpt(PseudoSingle, "", kind=HN)  # noqa: E741

    th = Cpt(SoftPositioner, limits=(-90, 90), init_pos=0, kind=HN)
    tth = Cpt(SoftPositioner, limits=(-170, 170), init_pos=0, kind=HN)

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            solver="no_op",
            geometry="TH TTH Q",
            **kwargs,
        )


class TwoC(DiffractometerBase):
    """Test case with custom names and additional axes."""

    # sorted alphabetically
    another = Cpt(PseudoSingle, "", kind=HN)  # noqa: E741
    q = Cpt(PseudoSingle, "", kind=HN)  # noqa: E741
    horizontal = Cpt(SoftPositioner, limits=(-10, 855), init_pos=0, kind=HN)
    theta = Cpt(SoftPositioner, limits=(-90, 90), init_pos=0, kind=HN)
    ttheta = Cpt(SoftPositioner, limits=(-170, 170), init_pos=0, kind=HN)
    vertical = Cpt(SoftPositioner, limits=(-10, 855), init_pos=0, kind=HN)

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            solver="th_tth",
            geometry="TH TTH Q",
            pseudos=["q"],
            reals="theta ttheta".split(),
            **kwargs,
        )
