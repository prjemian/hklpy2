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

    ~get_diffractometer
    ~list_samples
    ~new_lattice
    ~new_sample
    ~pa
    ~set_diffractometer
    ~wh
"""

from .diffract import DiffractometerBase
from .operations.lattice import Lattice

__all__ = """
    add_sample
    get_diffractometer
    list_samples
    pa
    set_diffractometer
    set_lattice
    wh
""".split()

import logging

logger = logging.getLogger(__name__)


class _SelectedDiffractometer:
    """
    Maintain the diffractometer selection.

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
):
    """Define a new crystal sample."""
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
        )
    return diffractometer.sample


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


def pa():
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
    _choice.diffractometer.wh(full=True)


def set_diffractometer(diffractometer: DiffractometerBase = None) -> None:
    """Declare the diffractometer to be used."""
    _choice.diffractometer = diffractometer


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


def wh():
    """
    Report (brief) where is the diffractometer.

    EXAMPLE::

        >>> wh()
        h=0, k=0, l=0
        wavelength=1.0
        omega=0, chi=0, phi=0, tth=0
    """
    _choice.diffractometer.wh(full=False)
