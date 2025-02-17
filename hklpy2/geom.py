"""
Diffractometer Geometries.

.. autosummary::

    ~diffractometer_class_factory
    ~diffractometer_factory

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
    ~SimulatedE6C_Psi
    ~SimulatedK4CV
    ~SimulatedK6C
    ~SimulatedTheta2Theta

.. rubric:: Special-Use Diffractometer Geometries
.. autosummary::

    ~ApsPolar
    ~Petra3_p09_eh2
    ~Petra3_p23_4c
    ~Petra3_p23_6c

.. rubric:: Support
.. autosummary::

    ~MixinSimulator
    ~MixinHkl
    ~MixinPsi
    ~MixinQ
"""

import logging

from ophyd import Component
from ophyd import Device
from ophyd import EpicsMotor
from ophyd import Kind
from ophyd import PseudoSingle
from ophyd import SoftPositioner

from .diffract import DiffractometerBase

__all__ = """
    diffractometer_class_factory
    diffractometer_factory
    ApsPolar
    E4CV
    E6C
    K4CV
    K6C
    MixinHkl
    MixinQ
    MixinSimulator
    Petra3_p09_eh2
    Petra3_p23_4c
    Petra3_p23_6c
    SimulatedE4CV
    SimulatedE6C
    SimulatedE6C_Psi
    SimulatedK4CV
    SimulatedK6C
    SimulatedTheta2Theta
    Theta2Theta
""".split()

logger = logging.getLogger(__name__)
H_OR_N = Kind.hinted | Kind.normal


def diffractometer_class_factory(
    *,
    solver: str = "hkl_soleil",
    geometry: str = "E4CV",
    solver_kwargs: dict = {"engine": "hkl"},
    reals: dict = {},
    motor_labels: list = ["motors"],
    class_name: str = "Hklpy2Diffractometer",
    class_bases: list = [DiffractometerBase],
):
    """
    Build a custom class for this diffractometer geometry.

    PARAMETERS

    solver : str
        Name of the backend solver providing the geometry. (default: '"hkl_soleil"')
    geometry : str
        Name of the diffractometer geometry. (default: '"E4CV"')
    solver_kwargs : str
        Additional configuration for the solver. (default: '{"engine": "hkl"}')
    reals : dict
        Specification of the real axis motors.  Dictionary keys are the motor
        names, values are the EPICS motor PV for that axis.  If the PV is
        'None', use a simulated positioner.

        The dictionary can be empty or must have exactly the canonical number of
        real axes.  The order of the axes is important.  The names provided will
        be mapped to the canonical order defined by the solver.

        (default: '{}' which means use the canonical names for the real axes and
        use simulated positioners)
    motor_labels : list
        Ophyd object labels for each real positioner. (default: '["motors"]')
    class_name : str
        Name to use for the diffractometer class.
        (default: '"Hklpy2Diffractometer"')
    class_bases : list
        List of base classes to use for the diffractometer class.
        (default: '[DiffractometerBase]')
    """
    from .operations.misc import solver_factory

    # The solver object describes its structure. Also verifies the solver is found.
    solver_object = solver_factory(solver, geometry, **solver_kwargs)

    class_attributes = {}
    for axis in solver_object.pseudo_axis_names:
        class_attributes[axis] = Component(PseudoSingle, "", kind=H_OR_N)
    real_names = solver_object.real_axis_names
    if len(reals) == len(solver_object.real_axis_names):
        real_names = list(reals)
    for axis in real_names:
        pv = reals.get(axis)
        if pv is None:
            attr = Component(
                SoftPositioner,
                limits=(-180, 180),
                init_pos=0,
                kind=H_OR_N,
                labels=motor_labels,
            )
        else:
            attr = Component(EpicsMotor, pv, kind=H_OR_N, labels=motor_labels)
        class_attributes[axis] = attr

    return type(class_name, tuple(class_bases), class_attributes)


def diffractometer_factory(
    *,
    prefix: str = "",
    name: str = "",
    solver: str = "hkl_soleil",
    geometry: str = "E4CV",
    solver_kwargs: dict = {"engine": "hkl"},
    reals: dict = {},
    motor_labels: list = ["motors"],
    labels: list = ["diffractometer"],
    class_name: str = "Hklpy2Diffractometer",
    class_bases: list = [DiffractometerBase],
    auto_assign: bool = True,
    **kwargs,
):
    """
    Factory function to create a diffractometer instance.

    EXAMPLES:

    Four-circle diffractometer, vertical orientation, Eulerian rotations,
    canonical real axis names, EPICS motor PVs::

        e4cv = diffractometer_factory(name="e4cv",
            solver="hkl_soleil", geometry="E4CV",
            reals=dict(omega="zgp:m1", chi="zgp:m2", phi="zgp:m3", tth="zgp:m4"),
        )

    Four-circle diffractometer, vertical orientation, Eulerian rotations,
    custom real axis names, simulated positioners::

        sim4c = diffractometer_factory(name="sim4c",
            solver="hkl_soleil", geometry="E4CV",
            reals=dict(uno=None, dos=None, tres=None, cuatro=None),
        )

    (Simplest case to get a simulator.)
    Four-circle diffractometer, vertical orientation, Eulerian rotations,
    canonical real axis names, simulated positioners (all default settings)::

        sim4c = diffractometer_factory(name="sim4c")

    Kappa six-circle diffractometer, simulated motors::

        simk6c = diffractometer_factory(name="simk6c",
            solver="hkl_soleil", geometry="K6C"
        )

    PARAMETERS

    prefix : str
        EPICS PV prefix (default: empty string)
    name : str
        Name of the ophyd diffractometer object to be created. (default: '""')
    solver : str
        Name of the backend solver providing the geometry. (default: '"hkl_soleil"')
    geometry : str
        Name of the diffractometer geometry. (default: '"E4CV"')
    solver_kwargs : str
        Additional configuration for the solver. (default: '{"engine": "hkl"}')
    reals : dict
        Specification of the real axis motors.  Dictionary keys are the motor
        names, values are the EPICS motor PV for that axis.  If the PV is
        'None', use a simulated positioner.

        The dictionary can be empty or must have exactly the canonical number of
        real axes.  The order of the axes is important.  The names provided will
        be mapped to the canonical order defined by the solver.

        (default: '{}' which means use the canonical names for the real axes and
        use simulated positioners)
    motor_labels : list
        Ophyd object labels for each real positioner. (default: '["motors"]')
    labels : list
        Ophyd object labels for the diffractometer object. (default: '["diffractometer"]')
    class_name : str
        Name to use for the diffractometer class.
        (default: '"Hklpy2Diffractometer"')
    class_bases : list
        List of base classes to use for the diffractometer class.
        (default: '[DiffractometerBase]')
    auto_assign : bool
        When 'True', call :meth:`~hklpy2.diffract.DiffractometerBase.auto_assign_axes()`.
        (default: 'True')
    kwargs : any
        Additional keyword arguments will be added when constructing
        the new diffractometer object.
    """
    DiffractometerClass = diffractometer_class_factory(
        solver=solver,
        geometry=geometry,
        solver_kwargs=solver_kwargs,
        reals=reals,
        motor_labels=motor_labels,
        class_name=class_name,
        class_bases=class_bases,
    )

    diffractometer = DiffractometerClass(
        prefix,
        name=name,
        solver=solver,
        geometry=geometry,
        solver_kwargs=solver_kwargs,
        labels=labels,
        **kwargs,
    )
    if auto_assign:
        diffractometer.auto_assign_axes()
    return diffractometer


# FIXME: Such definitions here trigger circular import errors.
# hkl_soleil solver
# SimulatedE4CV = diffractometer_class_factory(geometry="E4CV")
# SimulatedE6C = diffractometer_class_factory(geometry="E6C")
# SimulatedE6C_Psi = diffractometer_class_factory(geometry="E6C", solver_kwargs={"engine": "psi"})


class MixinSimulator(Device):
    """
    Mixin used by simulators.

    - Supplies default 'prefix' argument.
    - Automatically assigns diffractometer axes.
    """

    def __init__(self, prefix: str = "", **kwargs):
        super().__init__(prefix, **kwargs)
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

    h = Component(PseudoSingle, "", kind=H_OR_N)
    k = Component(PseudoSingle, "", kind=H_OR_N)
    l = Component(PseudoSingle, "", kind=H_OR_N)  # noqa: E741


class MixinPsi(Device):
    """
    Defines `psi` pseudo-positioner.
    """

    psi = Component(PseudoSingle, "", kind=H_OR_N)  # noqa: E741


class MixinQ(Device):
    """
    Defines `q` pseudo-positioner.
    """

    q = Component(PseudoSingle, "", kind=H_OR_N)  # noqa: E741


class ApsPolar(DiffractometerBase, MixinHkl):
    """
    6-circle, hkl_soleil, APS POLAR, engine="hkl".

    :class:`~hklpy2.backends.hkl_soleil.HklSolver`
    """

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            solver="hkl_soleil",
            geometry="APS POLAR",
            solver_kwargs={"engine": "hkl"},
            **kwargs,
        )


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


class SimulatedE4CV(MixinSimulator, E4CV, MixinHkl):
    """
    Eulerian 4-circle, hkl_soleil, E4CV, engine="hkl", simulated rotary axes.

    :class:`~hklpy2.backends.hkl_soleil.HklSolver`
    """

    omega = Component(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    chi = Component(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    phi = Component(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    tth = Component(SoftPositioner, limits=(-170, 170), init_pos=0, kind=H_OR_N)


class SimulatedE6C(MixinSimulator, E6C, MixinHkl):
    """
    Eulerian 6-circle, *hkl_soleil*, E6C, engine="hkl", simulated rotary axes.

    :class:`~hklpy2.backends.hkl_soleil.HklSolver`
    """

    mu = Component(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    omega = Component(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    chi = Component(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    phi = Component(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    gamma = Component(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    delta = Component(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)


class SimulatedE6C_Psi(MixinSimulator, DiffractometerBase, MixinPsi):
    """
    Eulerian 6-circle, *hkl_soleil*, E6C, engine="psi", simulated rotary axes.

    :class:`~hklpy2.backends.hkl_soleil.HklSolver`
    """

    mu = Component(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    omega = Component(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    chi = Component(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    phi = Component(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    gamma = Component(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    delta = Component(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)

    def __init__(self, prefix: str = "", **kwargs):
        super().__init__(
            prefix,
            solver="hkl_soleil",
            geometry="E6C",
            solver_kwargs={"engine": "psi"},
            **kwargs,
        )
        self.operator.auto_assign_axes()


class SimulatedK4CV(MixinSimulator, K4CV, MixinHkl):
    """
    Kappa 4-circle, hkl_soleil, K4CV, engine="hkl", simulated rotary axes.

    :class:`~hklpy2.backends.hkl_soleil.HklSolver`
    """

    komega = Component(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    kappa = Component(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    kphi = Component(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    tth = Component(SoftPositioner, limits=(-170, 170), init_pos=0, kind=H_OR_N)


class SimulatedK6C(MixinSimulator, K6C, MixinHkl):
    """
    Kappa 6-circle, hkl_soleil, K6C, engine="hkl", simulated rotary axes.

    :class:`~hklpy2.backends.hkl_soleil.HklSolver`
    """

    mu = Component(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    komega = Component(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    kappa = Component(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    kphi = Component(SoftPositioner, limits=(-180, 180), init_pos=0, kind=H_OR_N)
    gamma = Component(SoftPositioner, limits=(-170, 170), init_pos=0, kind=H_OR_N)
    delta = Component(SoftPositioner, limits=(-170, 170), init_pos=0, kind=H_OR_N)


class SimulatedTheta2Theta(MixinSimulator, Theta2Theta, MixinQ):
    """
    2-circle, *th_tth*, TH TTH Q, simulated rotary axes.

    NOTE:  For demonstration purposes.  Needs testing.

    :class:`~hklpy2.backends.th_tth_q.ThTthSolver`
    """

    theta = Component(SoftPositioner, limits=(-100, 100), init_pos=0, kind=H_OR_N)
    ttheta = Component(SoftPositioner, limits=(-15, 150), init_pos=0, kind=H_OR_N)
