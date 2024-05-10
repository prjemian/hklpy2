"""
A Solver connects |hklpy2| with a backend calculation library.

A :index:`!Solver` class (also described as a *backend*) is a
Python class that connects |hklpy2| with a library
that provides diffractometer geometries & calculations.
See the API documentation for details.

.. rubric:: Built-in Solvers

.. autosummary::

    ~hklpy2.backends.hkl_soleil.HklSolver
    ~hklpy2.backends.no_op.NoOpSolver
    ~hklpy2.backends.th_tth_q.ThTthSolver

.. rubric:: Base class for all solvers

.. autosummary::

    ~hklpy2.backends.base.SolverBase
"""

from .base import SolverBase  # noqa: F401
