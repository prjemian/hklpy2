"""
Lattice parameters for a single crystal.

.. autosummary::

    ~Lattice
    ~LatticeError
    ~SI_LATTICE_PARAMETER
    ~SI_LATTICE_PARAMETER_UNCERTAINTY
"""

import logging

from .. import Hklpy2Error
from .misc import compare_float_dicts

logger = logging.getLogger(__name__)

SI_LATTICE_PARAMETER = 5.431020511
"""
2018 CODATA recommended lattice parameter of silicon, Angstrom.

:see: https://physics.nist.gov/cgi-bin/cuu/Value?asil
"""

SI_LATTICE_PARAMETER_UNCERTAINTY = 0.000000089
"""
2018 CODATA reported uncertainty of :data:`SI_LATTICE_PARAMETER`.
"""


class LatticeError(Hklpy2Error):
    """Custom exceptions from the :mod:`hklpy2.operations.lattice` module."""


class Lattice:
    """
    Crystal lattice parameters.

    .. note:: Internal use only.

    EXAMPLE::

        import hklpy2
        hexagonal = hklpy2.Lattice(4.74, c=9.515, gamma=120)

    .. autosummary::

        ~_asdict
        ~__eq__
        ~__repr__
    """

    def __init__(
        self,
        a: float,
        b: float = None,
        c: float = None,
        alpha: float = 90.0,  # degrees
        beta: float = None,  # degrees
        gamma: float = None,  # degrees
        digits: int = 4,
    ):
        self.a = a
        self.b = b or a
        self.c = c or a
        self.alpha = alpha
        self.beta = beta or alpha
        self.gamma = gamma or alpha
        self.digits = digits

    def _asdict(self):
        """Return a new dict which maps lattice constant names and values."""
        # note: name is identical to namedtuple._asdict method
        return {
            "a": self.a,
            "b": self.b,
            "c": self.c,
            "alpha": self.alpha,
            "beta": self.beta,
            "gamma": self.gamma,
        }

    def __eq__(self, latt):
        """
        Compare two lattices for equality.

        EXAMPLE::

            lattice1 == lattice2
        """
        digits = min(self.digits, latt.digits)
        return compare_float_dicts(
            self._asdict(), latt._asdict(), min(self.digits, digits)
        )

    def __repr__(self):
        """
        Standard representation of lattice.
        """
        parameters = [f"{k}={round(v, self.digits)}" for k, v in self._asdict().items()]
        return "Lattice(" + ", ".join(parameters) + ")"

    # ---- get/set properties

    @property
    def digits(self) -> int:
        """Number of digits to display."""
        return self._digits

    @digits.setter
    def digits(self, value: int):
        self._digits = value
