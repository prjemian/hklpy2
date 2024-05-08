"""
Lattice parameters for a single crystal.

.. autosummary::

    ~Lattice
    ~LatticeError
    ~SI_LATTICE_PARAMETER
    ~SI_LATTICE_PARAMETER_UNCERTAINTY
"""

import math

from . import Hklpy2Error

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
    """Custom exceptions from the :mod:`hklpy2.lattice` module."""


class Lattice:
    """
    Crystal lattice parameters.

    EXAMPLE::

        import hklpy2
        hexagonal = hklpy2.Lattice(4.74, c=9.515, gamma=120)

    .. autosummary::

        ~equal
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
    ):
        self.a = a
        self.b = b or a
        self.c = c or a
        self.alpha = alpha
        self.beta = beta or alpha
        self.gamma = gamma or alpha

    def equal(self, latt, tolerance=1e-6):
        """
        Compare two lattices for equality, within given tolerance.

        EXAMPLE::

            lattice1.equal(lattice2)
        """

        def equivalent(us: float, them: float):
            return math.isclose(us, them, abs_tol=tolerance)

        return (
            equivalent(self.a, latt.a)
            and equivalent(self.b, latt.b)
            and equivalent(self.c, latt.c)
            and equivalent(self.alpha, latt.alpha)
            and equivalent(self.beta, latt.beta)
            and equivalent(self.gamma, latt.gamma)
        )

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
        Compare two lattices for equality, within default tolerance.

        EXAMPLE::

            lattice1 == lattice2
        """
        return self.equal(self, latt)

    def __repr__(self):
        """
        Standard representation of lattice.
        """
        parameters = [f"{k}={v}" for k, v in self._asdict().items()]
        return "Lattice(" + ", ".join(parameters) + ")"
