"""
Diffractometer Geometries.

.. rubric:: Geometries
.. autosummary::

    ~E4CV
    ~E6C
    ~K4CV
    ~K6C
    ~Theta2Theta

.. rubric:: Simulators
.. autosummary::

    ~SimulatedE4CV
    ~SimulatedE6C
    ~SimulatedK4CV
    ~SimulatedK6C
    ~SimulatedTheta2Theta

.. rubric:: Special-Use Diffractometer Geometries
.. autosummary::

    ~Petra3_p09_eh2
    ~Petra3_p23_4c
    ~Petra3_p23_6c

.. rubric:: Support
.. autosummary::

    ~MixinAutoAssignAxes
    ~MixinHkl
    ~MixinQ
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
    K4CV
    K6C
    MixinAutoAssignAxes
    MixinHkl
    MixinQ
    Petra3_p09_eh2
    Petra3_p23_4c
    Petra3_p23_6c
    SimulatedE4CV
    SimulatedE6C
    SimulatedK4CV
    SimulatedK6C
    SimulatedTheta2Theta
    Theta2Theta
""".split()

logger = logging.getLogger(__name__)
H_OR_N = Kind.hinted | Kind.normal


class MixinAutoAssignAxes(Device):
    """Automatically assigns diffractometer axes."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.operator.auto_assign_axes()


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


class E4CV(DiffractometerBase, MixinHkl):
    """
    Eulerian 4-circle, hkl_soleil, E4CV, engine="hkl".

    :class:`~hklpy2.backends.hkl_soleil.HklSolver`
    """

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            solver="hkl_soleil",
            geometry="E4CV",
            solver_kwargs={"engine": "hkl"},
            **kwargs,
        )


class E6C(DiffractometerBase, MixinHkl):
    """
    Eulerian 6-circle, hkl_soleil, E6C, engine="hkl".

    :class:`~hklpy2.backends.hkl_soleil.HklSolver`
    """

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            solver="hkl_soleil",
            geometry="E6C",
            solver_kwargs={"engine": "hkl"},
            **kwargs,
        )


class K4CV(DiffractometerBase, MixinHkl):
    """
    Kappa 4-circle, hkl_soleil, K4CV, engine="hkl".

    :class:`~hklpy2.backends.hkl_soleil.HklSolver`
    """

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            solver="hkl_soleil",
            geometry="K4CV",
            solver_kwargs={"engine": "hkl"},
            **kwargs,
        )


class K6C(DiffractometerBase, MixinHkl):
    """
    Kappa 6-circle, hkl_soleil, K6C, engine="hkl".

    :class:`~hklpy2.backends.hkl_soleil.HklSolver`
    """

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            solver="hkl_soleil",
            geometry="K6C",
            solver_kwargs={"engine": "hkl"},
            **kwargs,
        )


class Petra3_p09_eh2(DiffractometerBase, MixinHkl):
    """
    6-circle, hkl_soleil, PETRA3 P09 EH2, engine="hkl".

    :class:`~hklpy2.backends.hkl_soleil.HklSolver`
    """

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            solver="hkl_soleil",
            geometry="PETRA3 P09 EH2",
            solver_kwargs={"engine": "hkl"},
            **kwargs,
        )


class Petra3_p23_4c(DiffractometerBase, MixinHkl):
    """
    4-circle, hkl_soleil, PETRA3 P23 4C, engine="hkl".

    :class:`~hklpy2.backends.hkl_soleil.HklSolver`
    """

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            solver="hkl_soleil",
            geometry="PETRA3 P23 4C",
            solver_kwargs={"engine": "hkl"},
            **kwargs,
        )


class Petra3_p23_6c(DiffractometerBase, MixinHkl):
    """
    7-circle, hkl_soleil, PETRA3 P23 6C, engine="hkl".

    :class:`~hklpy2.backends.hkl_soleil.HklSolver`
    """

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            solver="hkl_soleil",
            geometry="PETRA3 P23 6C",
            solver_kwargs={"engine": "hkl"},
            **kwargs,
        )


class Theta2Theta(DiffractometerBase):
    """
    2-circle, th_tth, TH TTH Q.
    
    NOTE:  For demonstration purposes.  Needs testing.

    :class:`~hklpy2.backends.th_tth_q.ThTthSolver`
    """

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            solver="th_tth",
            geometry="TH TTH Q",
            **kwargs,
        )


class SimulatedE4CV(MixinAutoAssignAxes, E4CV, MixinHkl):
    """
    Eulerian 4-circle, hkl_soleil, E4CV, engine="hkl", simulated rotary axes.

    :class:`~hklpy2.backends.hkl_soleil.HklSolver`
    """

    omega = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    chi = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    phi = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    tth = Cpt(SoftPositioner, limits=(-170, 170), init_pos=0, kind=H_OR_N)


class SimulatedE6C(MixinAutoAssignAxes, E6C, MixinHkl):
    """
    Eulerian 6-circle, *hkl_soleil*, E6C, engine="hkl", simulated rotary axes.

    :class:`~hklpy2.backends.hkl_soleil.HklSolver`
    """

    mu = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    omega = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    chi = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    phi = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    gamma = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    delta = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)


class SimulatedK4CV(MixinAutoAssignAxes, K4CV, MixinHkl):
    """
    Kappa 4-circle, hkl_soleil, K4CV, engine="hkl", simulated rotary axes.

    :class:`~hklpy2.backends.hkl_soleil.HklSolver`
    """

    komega = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    kappa = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    kphi = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    tth = Cpt(SoftPositioner, limits=(-170, 170), init_pos=0, kind=H_OR_N)


class SimulatedK6C(MixinAutoAssignAxes, K6C, MixinHkl):
    """
    Kappa 6-circle, hkl_soleil, K6C, engine="hkl", simulated rotary axes.

    :class:`~hklpy2.backends.hkl_soleil.HklSolver`
    """

    mu = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    komega = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    kappa = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    kphi = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    gamma = Cpt(SoftPositioner, limits=(-170, 170), init_pos=0, kind=H_OR_N)
    delta = Cpt(SoftPositioner, limits=(-170, 170), init_pos=0, kind=H_OR_N)


class SimulatedTheta2Theta(MixinAutoAssignAxes, Theta2Theta, MixinQ):
    """
    2-circle, *th_tth*, TH TTH Q, simulated rotary axes.
    
    NOTE:  For demonstration purposes.  Needs testing.

    :class:`~hklpy2.backends.th_tth_q.ThTthSolver`
    """

    theta = Cpt(SoftPositioner, limits=(-100, 100), init_pos=0, kind=H_OR_N)
    ttheta = Cpt(SoftPositioner, limits=(-15, 150), init_pos=0, kind=H_OR_N)
