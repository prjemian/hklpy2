"""
Miscellaneous Support.

.. autosummary::

    ~check_value_in_list
    ~SOLVER_ENTRYPOINT_GROUP
    ~SolverError
    ~get_solver
    ~solvers
    ~solver_factory
    ~unique_name
"""

import logging
import uuid
from importlib.metadata import entry_points

from . import Hklpy2Error

logger = logging.getLogger(__name__)

SOLVER_ENTRYPOINT_GROUP = "hklpy2.solver"
"""Name by which |hklpy2| backend |solver| classes are grouped."""


class SolverError(Hklpy2Error):
    """Custom exceptions from a |solver|."""


def check_value_in_list(title, value, examples, blank_ok=False):
    """Raise KeyError exception if value is not in the list of examples."""
    if blank_ok:
        examples.append("")
    if value not in examples:
        msg = f"{title} {value!r} unknown. Pick one of: {examples!r}"
        raise KeyError(msg)


def get_solver(solver_name):
    """
    Load a Solver class from a named entry point.

    ::

        import hklpy2
        SolverClass = hklpy2.get_solver("hkl_soleil")
        libhkl_solver = SolverClass()
    """
    if solver_name not in solvers():
        raise SolverError(f"{solver_name=!r} unknown.  Pick one of: {solvers()!r}")
    entries = entry_points(group=SOLVER_ENTRYPOINT_GROUP)
    return entries[solver_name].load()


def solver_factory(
    solver_name: str,
    *,  # all kwargs must be specified by name
    geometry: str,
    pseudos: list = [],
    reals: list = [],
    extras: list = [],
    **kwargs,
):
    """
    Create a |solver| object with geometry and axes.
    """
    solver_class = get_solver(solver_name)
    return solver_class(
        geometry=geometry,
        pseudos=pseudos,
        reals=reals,
        extras=extras,
        **kwargs,
    )


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
