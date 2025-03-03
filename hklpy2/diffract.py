"""
Base class for all diffractometers

.. autosummary::

    ~DiffractometerBase
    ~pick_first_item
"""

import logging
import pathlib

import yaml
from ophyd import Component as Cpt
from ophyd import PseudoPositioner
from ophyd.pseudopos import pseudo_position_argument
from ophyd.pseudopos import real_position_argument
from ophyd.signal import AttributeSignal

from .operations.misc import DiffractometerError
from .operations.misc import load_yaml_file
from .operations.misc import roundoff
from .operations.reflection import Reflection
from .operations.sample import Sample
from .ops import Operations
from .wavelength_support import DEFAULT_WAVELENGTH
from .wavelength_support import MonochromaticXrayWavelength

__all__ = ["DiffractometerBase"]
logger = logging.getLogger(__name__)

DEFAULT_PHOTON_ENERGY_KEV = 8.0


def pick_first_item(now: tuple, solutions: list):
    """
    Choose first item from list.

    Used by '.forward()' method to pick the first solution
    from a list of possible solutions.

    User can provide an alternative function and assign to diffractometer's
    :meth:`~hklpy2.diffract.DiffractometerBase._forward_solution` method.

    .. rubric:: Parameters

    * ``now`` (*tuple*) : Current position.
    * ``solutions`` (*[tuple]*) : List of positions.
    """
    if len(solutions) == 0:
        raise DiffractometerError("No solutions.")
    return solutions[0]


class DiffractometerBase(PseudoPositioner):
    """
    Base class for all diffractometers.

    .. rubric:: Parameters

    *   ``solver`` (*str*) : Name of |solver| library.
        (default: unspecified)
    *   ``geometry``: (*str*) : Name of |solver| geometry.
        (default: unspecified)
    *   ``solver_kwargs`` (*dict*) : Any additional keyword arguments needed
        by |solver| library. (default: empty)
    *   ``pseudos`` ([str]) : List of diffractometer axis names to be used
        as pseudo axes. (default: unspecified)
    *   ``reals`` ([str]) : List of diffractometer axis names to be used as
        real axes. (default: unspecified)

    .. rubric:: (ophyd) Components

    .. rubric :: (ophyd) Attribute Components

    .. autosummary::

        ~geometry
        ~solver
        ~wavelength

    .. rubric:: Python Methods

    .. autosummary::

        ~add_reflection
        ~add_sample
        ~auto_assign_axes
        ~export
        ~forward
        ~full_position
        ~inverse
        ~move_dict
        ~move_forward_with_extras
        ~move_reals
        ~restore
        ~scan_extra
        ~wh

    .. rubric:: Python Properties

    .. autosummary::
        ~configuration
        ~pseudo_axis_names
        ~real_axis_names
        ~sample
        ~samples
        ~solver_name
    """

    # These two attributes are used by the PseudoPositioner class.
    # _pseudo = []  # List of pseudo-space objects.
    # _real = []  # List of real-space objects.
    # This code does NOT redefine them.

    geometry = Cpt(
        AttributeSignal,
        attr="operator.geometry",
        doc="Name of backend |solver| geometry.",
        write_access=False,
        kind="config",
    )
    """Name of backend |solver| geometry."""

    solver = Cpt(
        AttributeSignal,
        attr="solver_name",
        doc="Name of backend |solver| (library).",
        write_access=False,
        kind="config",
    )
    """Name of backend |solver| (library)."""

    wavelength = Cpt(
        AttributeSignal,
        attr="_source.wavelength",
        doc="Wavelength of incident radiation.",
        write_access=True,
        kind="config",
    )
    """Wavelength of incident radiation."""

    def __init__(
        self,
        prefix: str = "",
        *,
        solver: str = None,
        geometry: str = None,
        solver_kwargs: dict = {},
        pseudos: list[str] = None,
        reals: list[str] = None,
        **kwargs,
    ):
        self._backend = None
        self._forward_solution = pick_first_item
        self._source = MonochromaticXrayWavelength(DEFAULT_WAVELENGTH)

        self.operator = Operations(self)

        super().__init__(prefix, **kwargs)

        if isinstance(solver, str) and isinstance(geometry, str):
            self.operator.set_solver(solver, geometry, **solver_kwargs)

        self.operator.assign_axes(pseudos, reals)

    def add_reflection(
        self,
        pseudos,
        reals=None,
        wavelength=None,
        name=None,
        replace: bool = False,
    ) -> Reflection:
        """
        Add a new reflection with this geometry to the selected sample.

        .. rubric:: Parameters

        * ``pseudos`` (various): pseudo-space axes and values.
        * ``reals`` (various): dictionary of real-space axes and values.
        * ``wavelength`` (float): Wavelength of incident radiation.
          If ``None``, diffractometer's current wavelength will be assigned.
        * ``name`` (str): Reference name for this reflection.
          If ``None``, a random name will be assigned.
        * ``replace`` (bool): If ``True``, replace existing reflection of
          this name.  (default: ``False``)
        """
        return self.operator.add_reflection(
            pseudos, reals, wavelength or self.wavelength.get(), name, replace
        )

    def add_sample(
        self,
        name: str,
        a: float,
        b: float = None,
        c: float = None,
        alpha: float = 90.0,  # degrees
        beta: float = None,  # degrees
        gamma: float = None,  # degrees
        digits: int = 4,
        replace: bool = False,
    ) -> Sample:
        """Add a new sample."""
        return self.operator.add_sample(
            name,
            a,
            b,
            c,
            alpha,
            beta,
            gamma,
            digits,
            replace,
        )

    def auto_assign_axes(self):
        """
        Automatically assign diffractometer axes to this solver.

        .. seealso:: :meth:`hklpy2.ops.Operations.auto_assign_axes`

        A |solver| geometry specifies expected pseudo, real, and extra axes
        for its ``.forward()`` and ``.inverse()`` coordinate transformations.

        This method assigns this diffractometer's:

        *   first PseudoSingle axes
            to the pseudo axes expected by the selected |solver|.
        *   first Positioner axes (or subclass,
            such as EpicsMotor or SoftPositioner) to the real axes expected
            by the selected |solver|.
        *   any remaining PseudoSingle and Positioner axes to the
            extra axes expected by the selected |solver|.

        Any diffractometer axes not expected by the |solver| will
        not be assigned.
        """
        self.operator.auto_assign_axes()

    @property
    def configuration(self) -> dict:
        """Diffractometer configuration (orientation)."""
        return self.operator._asdict()

    @configuration.setter
    def configuration(self, config: dict) -> dict:
        """
        Diffractometer configuration (orientation).

        PARAMETERS

        config: dict
            Dictionary of diffractometer configuration, geometry, constraints,
            samples, reflections, orientations, solver, ...
        """
        return self.operator._fromdict(config)

    def export(self, file, comment=""):
        """
        Export the diffractometer configuration to a YAML file.

        Example::

            import hklpy2

            e4cv = hklpy2.creator(name="e4cv")
            e4cv.export("e4cv-config.yml", comment="example")
        """
        path = pathlib.Path(file)
        config = self.configuration
        config["_header"].update(dict(file=str(file), comment=str(comment)))
        dump = yaml.dump(
            config,
            indent=2,
            default_flow_style=False,
            sort_keys=False,
        )
        with open(path, "w") as y:
            y.write("#hklpy2 configuration file\n\n")
            y.write(dump)

    def restore(
        self,
        config,
        clear=True,
        restore_constraints=True,
        restore_wavelength=True,
    ):
        """
        Restore diffractometer configuration.

        Example::

            import hklpy2

            e4cv = hklpy2.creator(name="e4cv")
            e4cv.restore("e4cv-config.yml")

        PARAMETERS

        config *dict*, *str*, or *pathlib.Path* object:
            Dictionary with configuration, or name (str or pathlib object) of
            diffractometer configuration YAML file.
        clear *bool*:
            If ``True`` (default), remove any previous configuration of the
            diffractometer and reset it to default values before restoring the
            configuration.

            If ``False``, sample reflections will be append with all reflections
            included in the configuration data for that sample.  Existing
            reflections will not be changed.  The user may need to edit the
            list of reflections after ``restore(clear=False)``.
        restore_constraints *bool*:
            If ``True`` (default), restore any constraints provided.
        restore_wavelength *bool*:
            If ``True`` (default), restore wavelength.

        Note: Can't name this method "import", it's a reserved Python word.
        """
        if isinstance(config, (str, pathlib.Path)):
            config = load_yaml_file(config)
        if not isinstance(config, dict):
            raise TypeError(f"Unrecognized configuration: {config=}")
        header = config.get("_header")
        if header is None:
            raise KeyError("Configuration is missing '_header' key.")
        # Note: python_class key is not testable, could be anything.

        if restore_wavelength:
            self._source._fromdict(header)

        self.operator.configuration._fromdict(
            config,
            clear=clear,
            restore_constraints=restore_constraints,
        )

    @pseudo_position_argument
    def forward(self, pseudos: dict, wavelength: float = None) -> tuple:
        """Compute real-space coordinates from pseudos (hkl -> angles)."""
        logger.debug("forward: pseudos=%r", pseudos)
        solutions = self.operator.forward(pseudos, wavelength=wavelength)
        return self._forward_solution(self.real_position, solutions)

    def full_position(self, digits=4) -> dict:
        """Return dict with positions of pseudos, reals, & extras."""
        from .operations.misc import roundoff

        pdict = self.position._asdict()
        pdict.update(self.real_position._asdict())
        pdict.update(self.operator.solver.extras)
        for k in pdict:
            pdict[k] = roundoff(pdict[k], digits)
        return pdict

    @real_position_argument
    def inverse(self, reals: dict, wavelength: float = None) -> tuple:
        """Compute pseudo-space coordinates from reals (angles -> hkl)."""
        logger.debug("inverse: reals=%r", reals)
        pos = self.operator.inverse(reals, wavelength=wavelength)
        return self.PseudoPosition(**pos)  # as created by namedtuple

    def move_dict(self, axes: dict):
        """(plan) Move diffractometer axes as described in 'axes' dict."""
        from bluesky import plan_stubs as bps

        from .operations.misc import flatten_lists

        # Transform axes dict to args for bps.mv(position, value)
        moves = list(
            flatten_lists(
                [
                    [getattr(self, k), v]  # move the diffractometer axes
                    for k, v in axes._asdict().items()
                ]
            )
        )
        yield from bps.mv(*moves)

    def move_forward_with_extras(
        self,
        pseudos: dict,  # (h, k, l)
        extras: dict,  # (h2, k2, l2, psi)
    ):
        """
        (plan stub) Set extras and compute forward solution at fixed Q and extras.

        EXAMPLE::

            RE(
                move_forward_with_extras(
                    diffractometer,
                    Q=dict(h=2, k=1, l=0),
                    extras=dict(h2=2, k2=2, l2=0, psi=25),
                )
            )
        """
        # TODO:  #36
        self.operator.solver.extras = extras  # must come first
        solution = self.forward(list(pseudos.values()))
        yield from self.move_dict(solution)

    @real_position_argument
    def move_reals(self, real_positions) -> None:
        """(not a plan) Move the real-space axes as specified in 'real_positions'."""
        for axis_name in real_positions._fields:
            hkl_axis = getattr(self, axis_name)
            position = getattr(real_positions, axis_name)
            hkl_axis.move(position)

    def scan_extra(
        self,
        detectors: list,
        axis: str = None,  # name of extra parameter to be scanned
        start: float = None,
        finish: float = None,
        num: int = 2,
        *,
        pseudos: dict = None,  # h, k, l
        reals: dict = None,  # angles
        extras: dict = {},  # define all but the 'axis', these will remain constant
        fail_on_exception: bool = False,
        md: dict = None,
    ):
        """
        Scan one extra diffractometer parameter, such as 'psi'.

        * TODO: one **or more** (such as bp.scan)
        * TODO: support "inverse" transformation scan

        * iterate extra positions as decribed:
            * set extras
            * solution = forward(pseudos)
            * move to solution
            * acquire (trigger) all controls
            * read and record all controls
        """
        from collections.abc import Iterable

        import numpy
        from bluesky import plan_stubs as bps
        from bluesky import preprocessors as bpp

        from .operations.misc import dict_device_factory

        # validate
        if not isinstance(detectors, Iterable):
            raise TypeError(f"{detectors=} is not iterable.")
        if axis not in self.operator.solver.extra_axis_names:
            raise KeyError(f"{axis!r} not in {self.operator.solver.extra_axis_names}")
        if pseudos is None and reals is None:
            raise ValueError("Must define either pseudos or reals.")
        if pseudos is not None and reals is not None:
            raise ValueError("Cannot define both pseudos and reals.")

        if reals is not None:
            raise NotImplementedError("Inverse transformation.")  # FIXME: #37

        _md = {
            "diffractometer": {
                "name": self.name,
                "geometry": self.operator.solver.geometry,
                "engine": self.operator.solver.engine_name,
                "mode": self.operator.solver.mode,
                "extra_axes": self.operator.solver.extra_axis_names,
            },
            "axis": axis,
            "start": start,
            "finish": finish,
            "num": num,
            "pseudos": pseudos,
            "reals": reals,
            "extras": extras,
            "transformation": "forward" if reals is None else "inverse",
        }.update(md or {})

        extras[axis] = start
        extras_class = dict_device_factory(extras)
        extras_device = extras_class("", name=f"{self.name}_extras", kind="hinted")

        all_controls = detectors
        all_controls.append(extras_device)
        all_controls = list(set(all_controls))

        signal = getattr(extras_device, axis)  # Pick the 'axis' Component.
        signal.kind = "hinted"

        def position_series(start, finish, num):
            for value in numpy.linspace(start, finish, num=num):
                yield value

        @bpp.stage_decorator(detectors)
        @bpp.run_decorator(md=_md)
        def _inner():
            for value in position_series(start, finish, num):

                def move_axes(pseudos, reals, extras):
                    """Move extras, then reals or pseudos, move to the solution."""
                    if reals is None:
                        yield from self.move_forward_with_extras(pseudos, extras)
                    # else: # TODO: #37
                    #     yield from self.inverse_move_with_extras(reals, extras)

                def acquire(objects):
                    """Tell each object to acquire its data."""
                    group = "trigger_control_objects"
                    for item in objects:
                        yield from bps.trigger(item, group=group)
                    yield from bps.wait(group=group)

                def record(objects, stream="primary"):
                    """Read & record each object."""
                    yield from bps.create(stream)
                    for item in objects:
                        yield from bps.read(item)
                    yield from bps.save()

                # note the new axis position, will report later
                extras.update({axis: value})
                yield from bps.mv(signal, value)
                try:
                    yield from move_axes(pseudos, reals, extras)
                    yield from acquire(all_controls)
                    yield from record(all_controls)
                except Exception as reason:
                    if fail_on_exception:
                        raise reason
                    else:
                        print(f"FAIL: {axis}={value} {reason}")

        return (yield from _inner())

    # ---- get/set properties

    @property
    def pseudo_axis_names(self):
        """
        Names of all the pseudo axes, in order of appearance.

        Example::

            >>> fourc.pseudo_axis_names
            ['h', 'k', 'l']
        """
        return [o.attr_name for o in self.pseudo_positioners]

    @property
    def real_axis_names(self):
        """
        Names of all the real axes, in order of appearance.

        Example::

            >>> fourc.real_axis_names
            ['omega', 'chi, 'phi', 'tth']
        """
        return [o.attr_name for o in self.real_positioners]

    @property
    def samples(self):
        """Dictionary of samples."""
        if self.operator is None:
            return {}
        return self.operator.samples

    @property
    def sample(self):
        """Current sample object."""
        if self.operator is None:
            return None
        return self.operator.sample

    @sample.setter
    def sample(self, value: str) -> None:
        self.operator.sample = value

    @property
    def solver_name(self):
        """Backend |solver| library name."""
        if self.operator is not None and self.operator.solver is not None:
            return self.operator.solver.name
        return ""

    def wh(self, digits=4, full=False):
        """Concise report of the current diffractometer positions."""

        def wh_round(label, value):
            return f"{label}={roundoff(value, digits)}"

        def print_axes(names):
            print(", ".join([wh_round(nm, getattr(self, nm).position) for nm in names]))

        if full:
            print(f"diffractometer={self.name!r}")
            print(f"{self.operator.solver}")
            print(f"{self.sample!r}")
            for v in self.sample.reflections.values():
                print(f"{v}")
            print(f"Orienting reflections: {self.sample.reflections.order}")
            print(f"U={self.operator.solver.U}")
            print(f"UB={self.operator.solver.UB}")
            for v in self.operator.constraints.values():
                print(f"constraint: {v}")

        print_axes(self.pseudo_axis_names)
        print(f"wavelength={self.wavelength.get()}")
        print_axes(self.real_axis_names)

        extras = self.operator.solver.extras
        if len(extras) > 0:
            print(" ".join([wh_round(k, v) for k, v in extras.items()]))
