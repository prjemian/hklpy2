"""
A Solver connects |hklpy2| with a backend calculation library.

A backend (or solver) is a Python class that connects |hklpy2| with a library
backend that provides diffractometer capabilities.  See the API documentation
for details.

.. rubric:: Built-in Solvers

.. autosummary::

    ~hklpy2.backends.hkl_soleil.HklSolver
    ~hklpy2.backends.no_op.NoOpSolver

.. rubric:: Other support

.. autosummary::

    ~hklpy2.backends.abstract_solver.SolverBase
    ~hklpy2.backends.abstract_solver.setSolver
    ~hklpy2.backends.abstract_solver.solvers
    ~hklpy2.backends.abstract_solver.SOLVER_ENTRYPOINT_GROUP

"""

from .abstract_solver import SOLVER_ENTRYPOINT_GROUP  # noqa: F401
from .abstract_solver import SolverBase  # noqa: F401
from .abstract_solver import setSolver  # noqa: F401
from .abstract_solver import solvers  # noqa: F401
