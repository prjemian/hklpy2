"""
Diffractometer Geometries.

.. rubric:: Geometries
.. autosummary::

    ~E4CV
    ~E6C
    ~Theta2Theta

.. rubric:: Simulators
.. autosummary::

    ~SimulatedE4CV
    ~SimulatedE6C
    ~SimulatedTheta2Theta

.. rubric:: Support
.. autosummary::

    ~HklMixin

.. rubric:: Special-Use Diffractometer Geometries
"""

import logging

from ophyd import Component as Cpt
from ophyd import Device
from ophyd import Kind
from ophyd import PseudoSingle
from ophyd import SoftPositioner

from .diffract import DiffractometerBase

__all__ = """
    E4CV
    E6C
    MixinHkl
    MixinQ
    SimulatedE4CV
    SimulatedE6C
    SimulatedTheta2Theta
    Theta2Theta
""".split()

logger = logging.getLogger(__name__)
H_OR_N = Kind.hinted | Kind.normal


class MixinHkl(Device):
    """
    Defines `h`, `k`, & `l` pseudo-positioners.

    .. caution:: These comments need to be updated to |hklpy2|.

    Use this mixin class with any of the diffractometer geometries to create
    your own simulator.  Follow one of the simulators below, such as
    :class:`~hkl.geom.SimulatedE4CV`.  You should replace ``E4CV`` with your
    geometry's name.  And, you will need to create ``SoftPositioner`` components
    for each of the real-space axes, in the order required by that geometry.
    """

    h = Cpt(PseudoSingle, "", kind="hinted")
    k = Cpt(PseudoSingle, "", kind="hinted")
    l = Cpt(PseudoSingle, "", kind="hinted")  # noqa: E741


class MixinQ(Device):
    """
    Defines `q` pseudo-positioner.
    """

    q = Cpt(PseudoSingle, "", kind="hinted")  # noqa: E741


# TODO: Create a factory to make these hkl_soleil classes.
# "E4CV", (DiffractometerBase, HklMixin), ("hkl_soleil", "E4CV", engine="hkl")
# "E6C", (DiffractometerBase, HklMixin), ("hkl_soleil", "E6C", engine="hkl")


class E4CV(DiffractometerBase, MixinHkl):
    """
    4-circle, hkl_soleil, E4CV, engine="hkl".

    :class:`~hklpy2.backends.hkl_soleil.HklSolver`
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_solver("hkl_soleil", "E4CV", engine="hkl")


class E6C(DiffractometerBase, MixinHkl):
    """
    6-circle, hkl_soleil, E6C, engine="hkl".

    :class:`~hklpy2.backends.hkl_soleil.HklSolver`
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_solver("hkl_soleil", "E6C", engine="hkl")


class Theta2Theta(DiffractometerBase):
    """
    2-circle, th_tth, TH TTH Q.

    :class:`~hklpy2.backends.th_tth_q.ThTthSolver`
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_solver("th_tth", "TH TTH Q")


class SimulatedE4CV(E4CV, MixinHkl):
    """
    4-circle, hkl_soleil, E4CV, engine="hkl", simulated rotary axes.

    :class:`~hklpy2.backends.hkl_soleil.HklSolver`
    """

    omega = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    chi = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    phi = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    tth = Cpt(SoftPositioner, limits=(-170, 170), init_pos=0, kind=H_OR_N)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.operator.auto_assign_axes()


class SimulatedE6C(E4CV, MixinHkl):
    """
    6-circle, *hkl_soleil*, E6C, engine="hkl", simulated rotary axes.

    :class:`~hklpy2.backends.hkl_soleil.HklSolver`
    """

    mu = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    omega = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    chi = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    phi = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    gamma = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    delta = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.operator.auto_assign_axes()


class SimulatedTheta2Theta(Theta2Theta, MixinQ):
    """
    2-circle, *th_tth*, TH TTH Q, simulated rotary axes.

    :class:`~hklpy2.backends.th_tth_q.ThTthSolver`
    """

    theta = Cpt(SoftPositioner, limits=(-100, 100), init_pos=0, kind=H_OR_N)
    ttheta = Cpt(SoftPositioner, limits=(-15, 150), init_pos=0, kind=H_OR_N)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.operator.auto_assign_axes()
