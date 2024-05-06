"""
Backend: no_op

no reciprocal-space conversions

.. autosummary::

    ~NoOpSolver
"""

from .. import __version__


class NoOpSolver:
    """A backend solver that has no transformations for reciprocal space."""

    __version__ = __version__
