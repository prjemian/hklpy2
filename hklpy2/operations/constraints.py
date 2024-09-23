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
        "Return a nicely-formatted representation string."
        content = [f"{k}={v}" for k, v in self._asdict().items()]
        return f"{self.__class__.__name__}({', '.join(content)})"

    @abstractmethod
    def valid(self, **values: Dict[str, NUMERIC]) -> bool:
        """
        Is this constraint satisifed by current value(s)?

        PARAMETERS

        values *dict*: Dictionary of current axis: value pairs for comparison.
        """
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
    key : str
        Name of the axis for these limits.

    .. autosummary::

        ~valid
    """

    def __init__(self, low_limit=-180, high_limit=180, key=None):
        if key is None:
            raise ValueError("Must provide a value for 'key'.")

        self.key = key
        self._fields = "key low_limit high_limit".split()

        if low_limit is None:
            low_limit = -180
        if high_limit is None:
            high_limit = 180

        # fmt: off
        self.low_limit, self.high_limit = sorted(
            map(float, [low_limit, high_limit])
        )
        # fmt: on

    def __repr__(self) -> str:
        "Return a nicely-formatted representation string."
        return f"{self.low_limit} <= {self.key} <= {self.high_limit}"

    def valid(self, **values: Dict[str, NUMERIC]) -> bool:
        """
        True if low <= value <= high.

        PARAMETERS

        reals *dict*: Dictionary of current axis: value pairs for comparison.
        """
        if self.key not in values:
            raise KeyError(
                f"Supplied values ({values!r}) did not include this"
                f" constraint's key {self.key!r}."
            )

        return self.low_limit <= values[self.key] <= self.high_limit


class AxisConstraints:
    """
    Constraints for every (real) axis of the diffractometer.

    .. autosummary::

        ~_asdict
        ~valid
    """

    def __init__(self, reals: List[str]):
        self._db = [LimitsConstraint(key=k) for k in reals]

    def __len__(self) -> int:
        return len(self._db)

    def __str__(self) -> str:
        "Return content as a nicely-formatted string."
        return str([repr(c) for c in self._db])

    def _asdict(self):
        """Return a new dict which maps field names to their values."""
        return [c._asdict() for c in self._db]

    def valid(self, **reals: Dict[str, NUMERIC]) -> bool:
        """Are all constraints satisfied?"""
        findings = [constraint.valid(**reals) for constraint in self._db]
        return False not in findings
