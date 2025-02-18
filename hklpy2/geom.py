"""
Create a Diffractometer for any Geometry.

.. autosummary::

    ~diffractometer_class_factory
    ~creator
"""

import logging

from ophyd import Component
from ophyd import EpicsMotor
from ophyd import Kind
from ophyd import PseudoSingle
from ophyd import SoftPositioner

from .diffract import DiffractometerBase

__all__ = """
    diffractometer_class_factory
    creator
""".split()


logger = logging.getLogger(__name__)
H_OR_N = Kind.hinted | Kind.normal


def diffractometer_class_factory(
    *,
    solver: str = "hkl_soleil",
    geometry: str = "E4CV",
    solver_kwargs: dict = {"engine": "hkl"},
    pseudos: list = [],
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
    pseudos : list
        Specification of the names of any pseudo axis positioners
        in addition to the ones provided by the solver.

        (default: '[]' which means no additional pseudo axes)
    reals : dict
        Specification of the real axis motors.  Dictionary keys are the motor
        names, values are the EPICS motor PV for that axis.  If the PV is
        'None', use a simulated positioner.

        The dictionary can be empty or must have at least the canonical number of
        real axes.  The order of the axes is important.  The names provided will
        be mapped to the canonical order defined by the solver.  Components will
        be created for any extra *reals*.

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
    for axis in pseudos:
        if axis not in solver_object.pseudo_axis_names:
            class_attributes[axis] = Component(PseudoSingle, "", kind=H_OR_N)

    real_names = solver_object.real_axis_names
    if 0 < len(reals) < len(solver_object.real_axis_names):
        raise KeyError(f"Expected {len(real_names)} reals, received {reals}.")
    if len(reals) >= len(solver_object.real_axis_names):
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


def creator(
    *,
    prefix: str = "",
    name: str = "",
    solver: str = "hkl_soleil",
    geometry: str = "E4CV",
    solver_kwargs: dict = {"engine": "hkl"},
    pseudos: list = [],
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

        e4cv = creator(name="e4cv",
            solver="hkl_soleil", geometry="E4CV",
            reals=dict(omega="IOC:m1", chi="IOC:m2", phi="IOC:m3", tth="IOC:m4"),
        )

    Four-circle diffractometer, vertical orientation, Eulerian rotations,
    custom real axis names, simulated positioners::

        sim4c = creator(name="sim4c",
            solver="hkl_soleil", geometry="E4CV",
            reals=dict(uno=None, dos=None, tres=None, cuatro=None),
        )

    (Simplest case to get a simulator.)
    Four-circle diffractometer, vertical orientation, Eulerian rotations,
    canonical real axis names, simulated positioners (all default settings)::

        sim4c = creator(name="sim4c")

    Kappa six-circle diffractometer, simulated motors::

        simk6c = creator(name="simk6c",
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
    pseudos : list
        Specification of the names of any pseudo axis positioners
        in addition to the ones provided by the solver.

        (default: '[]' which means no additional pseudo axes)
    reals : dict
        Specification of the real axis motors.  Dictionary keys are the motor
        names, values are the EPICS motor PV for that axis.  If the PV is
        'None', use a simulated positioner.

        The dictionary can be empty or must have at least the canonical number of
        real axes.  The order of the axes is important.  The names provided will
        be mapped to the canonical order defined by the solver.  Components will
        be created for any extra *reals*.

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
        pseudos=pseudos,
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
