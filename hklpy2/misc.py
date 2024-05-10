"""
Miscellaneous Support.

.. autosummary::

    ~SOLVER_ENTRYPOINT_GROUP
    ~SolverError
    ~get_solver
    ~solvers
    ~unique_name
"""

import uuid
from importlib.metadata import entry_points

from . import Hklpy2Error

SOLVER_ENTRYPOINT_GROUP = "hklpy2.solver"
"""Name by which |hklpy2| backend |solver| classes are grouped."""


class SolverError(Hklpy2Error):
    """Custom exceptions from a |solver|."""


def get_solver(solver_name):
    """
    Load a Solver class from a named entry point.

    ::

        import hklpy2
        SolverClass = hklpy2.get_solver("hkl_soleil")
        libhkl_solver = SolverClass()
    """
    entries = entry_points(group=SOLVER_ENTRYPOINT_GROUP)
    return entries[solver_name].load()


def solvers():
    """
    Dictionary of available Solver classes, mapped by entry point name.

    ::

        import hklpy2
        print(hklpy2.solvers())
    """
    # fmt: off
    entries = {
        ep.name: ep.value
        for ep in entry_points(group=SOLVER_ENTRYPOINT_GROUP)
    }
    # fmt: on
    return entries


def unique_name(prefix=""):
    """Short, unique name, first 7 characters of a unique, random uuid."""
    return prefix + str(uuid.uuid4())[:7]
