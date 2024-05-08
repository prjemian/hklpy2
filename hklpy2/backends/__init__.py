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

    ~hklpy2.backends.base.SolverBase
    ~hklpy2.backends.base.get_solver
    ~hklpy2.backends.base.solvers
    ~hklpy2.backends.base.SOLVER_ENTRYPOINT_GROUP

"""

from .base import SOLVER_ENTRYPOINT_GROUP  # noqa: F401
from .base import SolverBase  # noqa: F401
from .base import get_solver  # noqa: F401
from .base import solvers  # noqa: F401
