"""
Lattice parameters for a single crystal.

Simplify for high-symmetry crystal systems.

EXAMPLES (highest to lowest symmetry):

=============== =============================== = = = ===== ==== =====
system          command                         a b c alpha beta gamma
=============== =============================== = = = ===== ==== =====
cubic           Lattice(5.)                     5 5 5 90    90   90
hexagonal       Lattice(4., c=3., gamma=120)    4 4 3 90    90   120
rhombohedral    Lattice(4., alpha=80.2)         4 4 4 80.2  80.2 80.2
tetragonal      Lattice(4, c=3)                 4 4 3 90    90   90
orthorhombic    Lattice(4, 5, 3)                4 5 3 90    90   90
monoclinic      Lattice(4, 5, 3, beta=75)       4 5 3 90    75   90
triclinic       Lattice(4, 5, 3, 75., 85., 95.) 4 5 3 75    85   95
=============== =============================== = = = ===== ==== =====

.. see: https://en.wikipedia.org/wiki/Crystal_system

.. autosummary::

    ~Lattice
"""

import math


class Lattice:
    """
    Crystal lattice parameters.

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

            lattice1.equal(lattice1)
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

            lattice1 == lattice1
        """
        return self.equal(self, latt)

    def __repr__(self):
        """
        Standard representation of lattice.
        """
        parameters = [f"{k}={v}" for k, v in self._asdict().items()]
        return "Lattice(" + ", ".join(parameters) + ")"
