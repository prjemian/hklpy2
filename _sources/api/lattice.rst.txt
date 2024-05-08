.. include:: /substitutions.txt

.. _api.lattice:

==================
Crystal Lattice
==================

Record a sample's crystalline :index:`!lattice` parameters: 
:math:`a, b, c, \alpha, \beta, \gamma`.  The 
:class:`~hklpy2.lattice.Lattice()` interface is 
simplified; it is not necessary to enter all parameters 
for high-symmetry crystal systems.

.. rubric:: Examples of the Seven 3-D Crystal Systems (highest to lowest symmetry)

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

:see: https://dictionary.iucr.org/Crystal_system
:see: https://en.wikipedia.org/wiki/Crystal_system

.. rubric:: EXAMPLES

::

    >>> from hklpy2 import Lattice
    >>> Lattice(5.)
    Lattice(a=5.0, b=5.0, c=5.0, alpha=90.0, beta=90.0, gamma=90.0)

    >>> Lattice(4., c=3., gamma=120)
    Lattice(a=4.0, b=4.0, c=3.0, alpha=90.0, beta=90.0, gamma=120)

    >>> Lattice(4., alpha=80.2)
    Lattice(a=4.0, b=4.0, c=4.0, alpha=80.2, beta=80.2, gamma=80.2)

    >>> Lattice(4, c=3)
    Lattice(a=4, b=4, c=3, alpha=90.0, beta=90.0, gamma=90.0)

    >>> Lattice(4, 5, 3)
    Lattice(a=4, b=5, c=3, alpha=90.0, beta=90.0, gamma=90.0)

    >>> Lattice(4, 5, 3, beta=75)
    Lattice(a=4, b=5, c=3, alpha=90.0, beta=75, gamma=90.0)

    >>> Lattice(4, 5, 3, 75., 85., 95.)
    Lattice(a=4, b=5, c=3, alpha=75.0, beta=85.0, gamma=95.0)

Source Code Documentation
-------------------------

.. automodule:: hklpy2.lattice
    :members:
    :private-members:
    :show-inheritance:
    :inherited-members:

