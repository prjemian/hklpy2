"""
Coordinates of a crystalline reflection.

Associates diffractometer angles (real-space) with crystalline reciprocal-space
(pseudo) coordinates.

.. autosummary::

    ~Reflection
    ~ReflectionError
    ~ReflectionsDict
"""

from . import Hklpy2Error
from . import SolverBase
from .misc import unique_name


class ReflectionError(Hklpy2Error):
    """Custom exceptions from the :mod:`hklpy2.reflection` module."""


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
        self.name = name or unique_name()
        self.solver = solver
        self.pseudos = pseudos
        self.angles = angles
        self.wavelength = wavelength
        # TODO: what about optional items (azimuth, h1, h2, zones, ...)

    def _asdict(self):
        """Describe the reflection as a dictionary."""
        return {
            "name": repr(self.name),
            "geometry": repr(self.solver.geometry),
            "pseudos": self.pseudos,
            "angles": self.angles,
            "wavelength": self.wavelength,
        }

    def __repr__(self):
        """
        Standard representation of reflection.
        """
        parameters = [f"{k}={v}" for k, v in self._asdict().items()]
        return "Reflection(" + ", ".join(parameters) + ")"

    # --------- get/set properties

    @property
    def angles(self):  # TODO: rename as reals?
        """Ordered dictionary of diffractometer's real-space axes."""
        return self._angles

    @angles.setter
    def angles(self, value):
        if not isinstance(value, dict):
            raise TypeError(f"Must supply dict, received angles={value!r}")
        # TODO: validate against self.solver.real_axis_names
        self._angles = value

    @property
    def name(self):
        """Sample name."""
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, (type(None), str)):
            raise TypeError(f"Must supply str, received name={value!r}")
        self._name = value

    @property
    def pseudos(self):
        """Ordered dictionary of diffractometer's reciprocal-space axes."""
        return self._pseudos

    @pseudos.setter
    def pseudos(self, value):
        if not isinstance(value, dict):
            raise TypeError(f"Must supply dict, received pseudos={value!r}")
        # TODO: validate against self.solver.pseudo_axis_names
        self._pseudos = value

    @property
    def solver(self):
        """Diffractometer |solver|."""
        return self._solver

    @solver.setter
    def solver(self, value):
        if not (isinstance(value, SolverBase) or issubclass(type(value), SolverBase)):
            raise TypeError(
                f"Must supply SolverBase() object, received solver={value!r}"
            )
        # note: calling SolverBase() will always generate a TypeError
        # "Can't instantiate abstract class SolverBase with abstract methods" ...
        self._solver = value

    @property
    def wavelength(self):
        """Wavelength of reflection."""
        return self._wavelength

    @wavelength.setter
    def wavelength(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError(f"Must supply number, received wavelength={value!r}")
        if value < 0:
            raise ValueError(f"Must be >=0, received wavelength={value}")
        self._wavelength = value


class ReflectionsDict(dict):
    """
    Dictionary of Reflections.

    .. autosummary::

        ~ordering
        ~setor
        ~set_orientation_reflections
        ~swap
    """

    ordering = []  # TODO: use get/set property?
    """List of ordering reflection names."""

    def set_orientation_reflections(self, reflections: [Reflection]) -> None:
        """Designate the order of the reflections to be used."""
        self.ordering = [r.name for r in reflections]

    setor = set_orientation_reflections
    """Common alias for :meth:`~set_orientation_reflections`."""

    def add(self, reflection: Reflection, overwrite: bool = False):
        """Add an orientation reflection."""
        if reflection.name in self and not overwrite:
            raise ReflectionError(
                f"Reflection {reflection.name!r} already defined. "
                "Set `overwrite=True` to replace it."
            )
        self[reflection.name] = reflection
        if reflection.name not in self.ordering:
            self.ordering.append(reflection.name)
        # TODO: remove any reflections from ordering that no longer exist

    def swap(self):
        """Swap the two named orientation reflections."""
        if len(self.ordering) < 2:
            raise ReflectionError("Need at least two reflections to swap.")
        rname1, rname2 = self.ordering[:2]
        self.ordering[0] = rname2
        self.ordering[1] = rname1
