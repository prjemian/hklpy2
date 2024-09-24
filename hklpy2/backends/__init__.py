"""
A Solver connects |hklpy2| with a backend calculation library.

A :index:`!Solver` class (also described as a *backend*) is a
Python class that connects |hklpy2| with a library
that provides diffractometer geometries & calculations.
See the API documentation for details.

.. rubric:: Built-in Solvers

.. autosummary::

    ~hkl_soleil.HklSolver
    ~no_op.NoOpSolver
    ~th_tth_q.ThTthSolver

.. rubric:: Base class for all solvers

.. autosummary::

    ~base.SolverBase
"""

from .base import SolverBase  # noqa: F401
