"""
Miscellaneous Support.

.. rubric: Functions
.. autosummary::

    ~check_value_in_list
    ~compare_float_dicts
    ~get_solver
    ~load_yaml
    ~load_yaml_file
    ~roundoff
    ~solver_factory
    ~solvers
    ~unique_name

.. rubric: Symbols
.. autosummary::

    ~IDENTITY_MATRIX_3X3
    ~SOLVER_ENTRYPOINT_GROUP

.. rubric: Custom Preprocessors
.. autosummary::

    ~ConfigurationRunWrapper

.. rubric: Custom Exceptions
.. autosummary::

    ~ConfigurationError
    ~ConstraintsError
    ~DiffractometerError
    ~LatticeError
    ~OperationsError
    ~ReflectionError
    ~SampleError
    ~SolverError
    ~WavelengthError
"""

import logging
import math
import pathlib
import uuid
from importlib.metadata import entry_points

import yaml

from .. import Hklpy2Error

logger = logging.getLogger(__name__)

IDENTITY_MATRIX_3X3 = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
"""Identity matrix, 2-D, 3 rows, 3 columns."""

SOLVER_ENTRYPOINT_GROUP = "hklpy2.solver"
"""Name by which |hklpy2| backend |solver| classes are grouped."""

# Custom exceptions


class ConfigurationError(Hklpy2Error):
    """Custom exceptions from :mod:`hklpy2.operations.configure`."""


class ConstraintsError(Hklpy2Error):
    """Custom exceptions from :mod:`hklpy2.operations.constraints`."""


class DiffractometerError(Hklpy2Error):
    """Custom exceptions from :class:`~DiffractometerBase`."""


class LatticeError(Hklpy2Error):
    """Custom exceptions from :mod:`hklpy2.operations.lattice`."""


class OperationsError(Hklpy2Error):
    """Custom exceptions from :class:`~Operations`."""


class ReflectionError(Hklpy2Error):
    """Custom exceptions from :mod:`hklpy2.operations.reflection`."""


class SampleError(Hklpy2Error):
    """Custom exceptions from :mod:`hklpy2.operations.sample`."""


class SolverError(Hklpy2Error):
    """Custom exceptions from a |solver|."""


class WavelengthError(Hklpy2Error):
    """Custom exceptions from :mod:`hklpy2.wavelength_support`."""


# Custom preprocessors


class ConfigurationRunWrapper:
    """
    Write configuration of supported device(s) to a bluesky run.

    EXAMPLE::

        crw = ConfigurationRunWrapper(sim4c2)
        RE.preprocessors.append(crw.wrapper)
        RE(bp.rel_scan([noisy], m1, -1.2, 1.2, 11))

    Disable the preprocessor::

        crw.enable = False  # 'True' to enable

    Remove the last preprocessor::

        RE.preprocessors.pop()

    Add another diffractometer::

        crw.devices.append(e4cv)

    .. autosummary::

        ~device_names
        ~devices
        ~enable
        ~known_bases
        ~start_key
        ~validate
        ~wrapper
    """

    devices = []
    """List of devices to be reported."""

    known_bases = []
    """
    Known device base classes.

    Any device (base class) that reports its configuration dictionary in
    the `.read_configuration()` method can be added to this tuple.
    """

    start_key = "diffractometers"
    """Top-level key in run's metadata dictionary."""

    def __init__(self, *devices, knowns=None):
        """
        Constructor.

        EXAMPLES::

            ConfigurationRunWrapper(sim4c)
            ConfigurationRunWrapper(e4cv, e6c)

        PARAMETERS

        devices : list
            List of supported objects to be reported.
        knowns : list
            List of base classes that identify supported objects.
            (default: :class:`hklpy2.DiffractometerBase`)
        """
        from .. import DiffractometerBase as hklpy2_DiffractometerBase

        self.enable = True
        self.known_bases = knowns or [hklpy2_DiffractometerBase]
        self.validate(devices)
        self.devices = list(devices)

    @property
    def device_names(self) -> [str]:
        """Return list of configured device names."""
        return [dev.name for dev in self.devices]

    @property
    def enable(self) -> bool:
        """Is it permitted to write device configuration?"""
        return self._enable

    @enable.setter
    def enable(self, state: bool) -> None:
        """Set permit to write configuration."""
        self._enable = state

    def validate(self, devices) -> None:
        """Verify all are recognized objects."""
        for dev in devices:
            if not isinstance(dev, tuple(self.known_bases)):
                raise TypeError(f"{dev} is not a recognized object.")

    def wrapper(self, plan):
        """
        Bluesky plan wrapper (preprocessor).

        Writes device(s) configuration to start document metadata.

        Example::

            crw = ConfigurationRunWrapper(e4cv)
            RE.preprocessors.append(crw.wrapper)
        """
        from bluesky import preprocessors as bpp

        if not self._enable or len(self.devices) == 0:
            # Nothing to do here, move on.
            return (yield from plan)

        self.validate(self.devices)

        # TODO: consider allowing ophyd-async to succeed, too
        # cfg = {}
        # for dev in self.devices:
        #     cdict = yield from bps.configure(dev)
        #     cfg[dev.name] = cdict[-1]

        cfg = {
            dev.name: dev.read_configuration()
            # orientation details
            for dev in self.devices
        }
        return (yield from bpp.inject_md_wrapper(plan, {self.start_key: cfg}))


# Functions


def check_value_in_list(title, value, examples, blank_ok=False):
    """Raise ValueError exception if value is not in the list of examples."""
    if blank_ok:
        examples.append("")
    if value not in examples:
        msg = f"{title} {value!r} unknown. Pick one of: {examples!r}"
        raise ValueError(msg)


def compare_float_dicts(a1, a2, tol=1e-4):
    """
    Compare two dictionaries.  Values are all floats.
    """
    if tol <= 0:
        raise ValueError("received {tol=}, should be tol >0")

    if sorted(a1.keys()) != sorted(a2.keys()):
        return False

    tests = [True]
    for k, v in a1.items():
        if isinstance(v, float):
            if tol < 1:
                test = math.isclose(a1[k], a2[k], abs_tol=tol)
            else:
                test = round(a1[k], tol) == round(a2[k], tol)
        else:
            test = a1[k] == a2[k]
        if not test:
            return False  # no need to go further
    return False not in tests


def get_solver(solver_name):
    """
    Load a Solver class from a named entry point.

    ::

        import hklpy2
        SolverClass = hklpy2.get_solver("hkl_soleil")
        libhkl_solver = SolverClass()
    """
    if solver_name not in solvers():
        raise SolverError(f"{solver_name=!r} unknown.  Pick one of: {solvers()!r}")
    entries = entry_points(group=SOLVER_ENTRYPOINT_GROUP)
    return entries[solver_name].load()


def load_yaml(text: str):
    """Load YAML from text."""
    return yaml.load(text, yaml.Loader)


def load_yaml_file(file):
    """Return contents of a YAML file as a Python object."""
    path = pathlib.Path(file)
    if not path.exists():
        raise FileExistsError(f"YAML file '{path}' does not exist.")
    return load_yaml(open(path, "r").read())


def roundoff(value, digits=4):
    """Round a number to specified precision."""
    return round(value, ndigits=digits) or 0  # "-0" becomes "0"


def solver_factory(solver_name: str, geometry: str, **kwargs):
    """
    Create a |solver| object with geometry and axes.
    """
    solver_class = get_solver(solver_name)
    return solver_class(geometry, **kwargs)


def solvers():
    """
    Dictionary of available Solver classes, mapped by entry point name.

    ::

        import hklpy2
        print(hklpy2.solvers())
    """
    # fmt: off
    entries = {
        ep.name: ep.value
        for ep in entry_points(group=SOLVER_ENTRYPOINT_GROUP)
    }
    # fmt: on
    return entries


def unique_name(prefix="", length=7):
    """
    Short, unique name, first 7 (at most) characters of a unique, random uuid.
    """
    return prefix + str(uuid.uuid4())[: max(1, min(length, 7))]
