"""
Coordinates of a crystalline reflection.

Associates diffractometer angles (real-space) with crystalline reciprocal-space
(pseudo) coordinates.

.. autosummary::

    ~Reflection
    ~ReflectionError
    ~ReflectionsDict
"""

from .misc import uuid7


class ReflectionError(Exception):
    """Any exception from the Reflection() class."""


class Reflection:
    """
    Coordinates real and pseudo axes.

    EXAMPLE::

        import hklpy2
        r1 = hklpy2.Reflection(...)  # TODO

    .. autosummary::

        ~_asdict
        ~name
    """

    def __init__(
        self, solver, pseudos: dict, angles: dict, wavelength: float, name=None
    ) -> None:
        self.name = name or uuid7()
        self.solver = solver
        self.angles = angles
        self.pseudos = pseudos
        self.wavelength = wavelength

    def _asdict(self):
        """Describe the reflection as a dictionary."""
        return {
            "name": repr(self.name),
            "pseudos": self.pseudos,
            "angles": self.angles,
            "wavelength": self.wavelength,
            "geometry": repr(self.solver.gname),
        }

    def __repr__(self):
        """
        Standard representation of reflection.
        """
        parameters = [f"{k}={v}" for k, v in self._asdict().items()]
        return "Reflection(" + ", ".join(parameters) + ")"

    # --------- get/set properties

    @property
    def name(self):
        """Sample name."""
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name


class ReflectionsDict(dict):
    """
    Dictionary of Reflections.

    .. autosummary::

        ~ordering
        ~set_orientation_reflections
        ~set_or
        ~swap
    """

    ordering = []
    """List of ordering reflection names."""

    def set_orientation_reflections(self, r1: Reflection, r2: Reflection):
        """Designate r1 & r2 as the two named reflections."""
        self.ordering = [r1.name, r2.name]

    set_or = set_orientation_reflections
    """Common alias for :meth:`~set_orientation_reflections`."""

    def swap(self):
        """Swap the two named orientation reflections."""
        if len(self.ordering) < 2:
            raise ReflectionError("Need at least two reflections to swap.")
        rname1, rname2 = self.ordering[:2]
        self.ordering[0] = rname2
        self.ordering[1] = rname1
