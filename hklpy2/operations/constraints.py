"""
Limitations on acceptable positions from computed 'forward()' solutions.

.. autosummary::

    ~AxisConstraints
    ~ConstraintBase
    ~LimitsConstraint

From **hklpy**, these TODO items:

- _constraints_dict
- _constraints_for_databroker
- _push_current_constraints
- _set_constraints
"""

from abc import ABC
from abc import abstractmethod
from typing import Dict
from typing import List
from typing import Union

NUMERIC = Union[int, float]


class ConstraintBase(ABC):
    """
    Base class for all constraints for selecting 'forward()' solutions.

    .. autosummary::

        ~_asdict
        ~valid
    """

    _fields: List[str] = []

    def _asdict(self):
        """Return a new dict which maps field names to their values."""
        return {k: getattr(self, k) for k in self._fields}

    def __repr__(self) -> str:
        "Return a nicely formatted representation string."
        content = [f"{k}={v}" for k, v in self._asdict().items()]
        return f"{self.__class__.__name__}({', '.join(content)})"

    @abstractmethod
    def valid(self, value: NUMERIC) -> bool:
        """Does value satisfy this constraint?"""
        return True


class LimitsConstraint(ConstraintBase):
    """
    Value must fall between low & high limits.

    Parameters
    ----------
    low_limit : float
        Lowest acceptable value for this axis when computing real-space solutions
        from given reciprocal-space positions.
    high_limit : float
        Highest acceptable value for this axis when computing real-space solutions
        from given reciprocal-space positions.

    .. autosummary::

        ~valid
    """

    def __init__(self, low_limit=-180, high_limit=180):
        if low_limit is None:
            low_limit = -180
        if high_limit is None:
            high_limit = 180
        limits = list(map(float, [low_limit, high_limit]))
        self.low_limit = min(limits)
        self.high_limit = max(limits)
        self._fields = "low_limit high_limit".split()

    def valid(self, value: NUMERIC) -> bool:
        """True if low <= value <= high."""
        return self.low_limit <= value <= self.high_limit


class AxisConstraints:
    """
    Constraints for every (real) axis of the diffractometer.

    .. autosummary::

        ~_asdict
        ~valid
    """

    def __init__(self, reals: List[str] ):
        self.axes = {k: [LimitsConstraint()] for k in reals}
        self.stack = []  # TODO:

    def _asdict(self):
        """Return a new dict which maps field names to their values."""
        return {k: [c._asdict() for c in self.axes[k]] for k in self.axes.keys()}

    def valid(self, **reals: Dict[str, NUMERIC]) -> bool:
        """Do all axis values satisfy their constraints?"""
        if sorted(reals.keys()) != sorted(self.axes.keys()):
            raise KeyError(f"Must use the same keys: {list(self.axes.keys())}")

        for key, value in reals.items():
            for constraint in self.axes[key]:
                if not constraint.valid(value):
                    return False

        return True
