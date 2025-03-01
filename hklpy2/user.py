"""
Simplified interface for |hklpy2| diffractometer users.

The user must define a diffractometer object, then
register that object here.  For example::

    from hklpy2 import creator
    from hkl.user import *

    e4cv = creator(name="e4cv")
    set_diffractometer(e4cv)
    wh()
    pa()

FUNCTIONS

.. autosummary::

    ~add_reflection
    ~add_sample
    ~cahkl
    ~cahkl_table
    ~calc_UB
    ~get_diffractometer
    ~list_samples
    ~or_swap
    ~pa
    ~set_diffractometer
    ~set_energy
    ~set_lattice
    ~setor
    ~wh
"""

from collections import namedtuple

from .diffract import DiffractometerBase
from .operations.lattice import Lattice
from .wavelength_support import MonochromaticXrayWavelength

# TODO: remove_sample, remove_reflection
# TODO: setor alias to add_reflection
# TODO: pa() should identify reflections used to compute UB

__all__ = """
    add_reflection
    add_sample
    cahkl
    cahkl_table
    calc_UB
    get_diffractometer
    list_samples
    or_swap
    pa
    set_diffractometer
    set_energy
    set_lattice
    setor
    wh
""".split()

import logging

logger = logging.getLogger(__name__)


class _SelectedDiffractometer:
    """
    Module class to maintain the diffractometer selection.

    .. autosummary::

        ~_selection
        ~diffractometer
    """

    _selection = None
    """The current diffractometer."""

    @property
    def diffractometer(self) -> DiffractometerBase:
        if self._selection is None:
            raise ValueError(
                "No diffractometer selected."
                " Call 'set_diffractometer(diffr)' where"
                " 'diffr' is a diffractometer instance."
            )
        return self._selection

    @diffractometer.setter
    def diffractometer(self, diffractometer: DiffractometerBase) -> None:
        """Name the diffractometer to be used."""
        if not isinstance(diffractometer, DiffractometerBase):
            if diffractometer is not None:
                raise TypeError(
                    f"{diffractometer} must be an hklpy2 'DiffractometerBase' subclass."
                )
        self._selection = diffractometer


_choice = _SelectedDiffractometer()  # selected diffractometer geometry


def add_sample(
    name: str,
    a: float,
    b: float = None,
    c: float = None,
    alpha: float = 90,
    beta: float = None,
    gamma: float = None,
    digits: int = 4,
    replace: bool = False,
):
    """Add a new crystal sample."""
    diffractometer = _choice.diffractometer
    if name in diffractometer.samples:
        logger.warning(
            (
                f"Sample {name!r} is already defined."
                "  Add 'replace=True' to redefine this sample name."
                "  Call 'set_lattice(a, ...)' to define a new lattice."
            ),
        )
    else:
        diffractometer.add_sample(
            name,
            a,
            b=b,
            c=c,
            alpha=alpha,
            beta=beta,
            gamma=gamma,
            digits=digits,
            replace=replace,
        )
    return diffractometer.sample


def cahkl(h, k, l):  # noqa: E741
    """
    Calculate motor positions for one reflection - DOES NOT MOVE motors.

    Returns a namedtuple.
    """
    diffractometer = get_diffractometer()
    position = namedtuple("Position", "h k l".split())(h, k, l)
    solutions = diffractometer.operator.forward(position)
    return diffractometer._forward_solution(diffractometer.real_position, solutions)


def cahkl_table(*reflections, digits=5):
    """
    Return a table with motor positions for each reflection given.

    Parameters
    ----------
    reflections : list(tuple(number,number,number))
        This is a list of reflections where
        each reflection is a tuple of 3 numbers
        specifying (h, k, l) of the reflection
        to compute the ``forward()`` computation.

        Example:  ``[(1,0,0), (1,1,1)]``
    digits : int
        Number of digits to roundoff each position
        value.  Default is 5.
    """
    operator = get_diffractometer().operator
    HklPosition = namedtuple("HklPosition", "h k l".split())  # TODO: #36
    reflections = [HklPosition(*r) for r in reflections]
    return operator.forward_solutions_table(reflections, digits=digits)


def calc_UB(r1, r2, wavelength=None):
    """Compute the UB matrix with two reflections."""
    return get_diffractometer().operator.calc_UB(r1, r2)


def get_diffractometer():
    """Return the currently-selected diffractometer (or ``None``)."""
    try:
        return _choice.diffractometer
    except ValueError:
        return None


def list_samples(full=False):
    """
    Print all defined crystal samples, current sample first.

    EXAMPLE::

        In [5]: list_samples()
        > Sample(name='vibranium', lattice=Lattice(a=6.2832, system='cubic'))
        Sample(name='sample', lattice=Lattice(a=1, system='cubic'))
    """

    def display(sample, preface=""):
        if full:
            print(f"{preface}{sample}")
        else:
            print(f"{preface}{sample!r}")

    diffractometer = _choice.diffractometer
    current_sample = diffractometer.sample

    # always show the default sample first
    display(current_sample, "> ")

    # now, show any other samples
    for sample in diffractometer.samples.values():
        if sample != current_sample:
            preface = "\n" if full else ""
            display(sample, preface)


def or_swap():
    """
    Swap the first 2 [UB] reflections, re-compute & return new [UB].

    .. note:: The SPEC user community knows this function as ``or_swap``.

    Example::

        # define 2 reflections
        r400 = hkl.user.setor(4, 0, 0, tth=69.0966, omega=-145.451, chi=0, phi=0, wavelength=1.54)
        r040 = hkl.user.setor(0, 4, 0, tth=69.0966, omega=-145.451, chi=0, phi=90, wavelength=1.54)
        # calculate UB
        hkl.user.calc_UB(r400, r040)
        # swap the two reflections (and recalculate UB)
        hkl.user.or_swap()
    """
    diffractometer = _choice.diffractometer
    reflections = diffractometer.sample.reflections.swap()[:2]
    return calc_UB(*reflections)


def pa(digits=4):
    """
    Report (all) the diffractometer settings.

    EXAMPLE::

        >>> pa()
        diffractometer='e4cv'
        HklSolver(name='hkl_soleil', version='5.1.2', geometry='E4CV', engine_name='hkl', mode='bissector')
        Sample(name='vibranium', lattice=Lattice(a=6.2832, system='cubic'))
        U=[[0.000278604397, -0.99999996119, -3.9081e-08], [1.6307e-08, 3.9086e-08, -1.0], [0.99999996119, 0.000278604397, 1.6317e-08]]
        UB=[[0.000278604432, -0.999999952659, -1.87102e-07], [1.6307e-08, 3.9086e-08, -1.000000171333], [1.000000087947, 0.000279360313, -1.88574e-07]]
        Reflection(name='r400', geometry='E4CV', pseudos={'h': 4, 'k': 0, 'l': 0}, reals={'omega': -145.451, 'chi': 0, 'phi': 0, 'tth': 69.066}, wavelength=1.54, digits=4)
        Reflection(name='r040', geometry='E4CV', pseudos={'h': 0, 'k': 4, 'l': 0}, reals={'omega': -145.451, 'chi': 0, 'phi': 90, 'tth': 69.066}, wavelength=1.54, digits=4)
        Reflection(name='r004', geometry='E4CV', pseudos={'h': 0, 'k': 0, 'l': 4}, reals={'omega': -145.451, 'chi': 90, 'phi': 0, 'tth': 69.066}, wavelength=1.54, digits=4)
        constraint: -180.2 <= omega <= 180.2
        constraint: -180.2 <= chi <= 180.2
        constraint: -180.2 <= phi <= 180.2
        constraint: -180.2 <= tth <= 180.2
        h=0, k=0, l=0
        wavelength=1.54
        omega=0, chi=0, phi=0, tth=0
    """
    _choice.diffractometer.wh(digits=digits, full=True)


def set_diffractometer(diffractometer: DiffractometerBase = None) -> None:
    """Declare the diffractometer to be used."""
    _choice.diffractometer = diffractometer


def set_energy(value, units=None, offset=None):
    """
    Set the energy (thus wavelength) to be used (does not change control system value).
    """

    source = _choice.diffractometer._source
    if not isinstance(source, MonochromaticXrayWavelength):
        raise TypeError(
            f"'set_energy()' not supported for {source!r},"
            f" requires {MonochromaticXrayWavelength}."
        )
    # No ophyd objects in this module.  These are float values using properties.
    if units is not None:
        source.energy_units = units
    if offset is not None:
        source.energy_offset = offset  # TODO: requires feature addition
        raise NotImplementedError(
            "Monochromatic source energy offset not implemented (yet)."
        )
    source.energy = value


def set_lattice(
    a: float,
    b: float = None,
    c: float = None,
    alpha: float = 90,
    beta: float = None,
    gamma: float = None,
    digits: int = 4,
):
    """Redefine the sample's lattice."""
    _choice.diffractometer.sample.lattice = Lattice(
        a,
        b=b,
        c=c,
        alpha=alpha,
        beta=beta,
        gamma=gamma,
        digits=digits,
    )


def setor(h, k, l, *reals, wavelength=None, name=None, **kwreals):  # noqa: E741
    """
    (aka ``add_reflection``) Define a crystal reflection and its motor positions.

    * Positions:

      * Can be omitted (use current values from diffractometer)
      * Specified by values.  Must use expected order.
      * Specified by names.  Can appear in any order.

    * wavelength: when not specified, use the current diffractometer value.
    * name: when not specified, make up a new name.

    EXAMPLES::

        In [9]: setor(4, 0, 0)
        Out[9]: Reflection(name='r4', geometry='E4CV', pseudos={'h': 4, 'k': 0, 'l': 0},
            reals={'omega': -145.451, 'chi': 0, 'phi': 0, 'tth': 69.0966}, wavelength=1.54, digits=4)

        In [11]: setor(0, 4, 0, -145.451, 0, 90, 69.0966, name="r040")
        Out[11]: Reflection(name='r040', geometry='E4CV', pseudos={'h': 0, 'k': 4, 'l': 0},
            reals={'omega': -145.451, 'chi': 0, 'phi': 90, 'tth': 69.0966}, wavelength=1.54, digits=4)

        In [11]: setor(0, 0, 4 omega=-145.451, chi=90, phi=0, tth=69.0966, name="r004")
        Out[11]: Reflection(name='r004', geometry='E4CV', pseudos={'h': 0, 'k': 0, 'l': 4},
            reals={'omega': -145.451, 'chi': 90, 'phi': 0, 'tth': 69.0966}, wavelength=1.54, digits=4)

    """
    diffractometer = _choice.diffractometer
    if len(reals) > 0:  # Real motor positions as values in expected order.
        # NOTE: Will ignore any kwreals.
        rpos = reals
    elif len(kwreals) > 0:  # Real motor positions specified as dict, in any order.
        rpos = [
            kwreals[axis]
            for axis in diffractometer.real_axis_names  # in expected order
            if axis in kwreals  # only if specified
        ]
    else:
        rpos = diffractometer.real_position

    # NOTE: hkl_soleil/libhkl gets the wavelength on a reflection from the diffractometer.
    # When the wavelength is set, it calls libhkl directly.
    # as self._geometry.wavelength_set(wavelength, self._units)
    # The code here uses that procedure.
    if wavelength not in (None, 0):
        diffractometer._source.wavelength = wavelength

    name = name or f"r{1 + len(diffractometer.sample.reflections)}"
    refl = diffractometer.add_reflection((h, k, l), reals=rpos, name=name)
    return refl


def wh(digits=4):
    """
    Report (brief) where is the diffractometer.

    EXAMPLE::

        >>> wh()
        h=0, k=0, l=0
        wavelength=1.0
        omega=0, chi=0, phi=0, tth=0
    """
    _choice.diffractometer.wh(digits=digits, full=False)


add_reflection = setor
