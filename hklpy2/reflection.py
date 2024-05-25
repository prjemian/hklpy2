"""
Coordinates of a crystalline reflection.

Associates diffractometer angles (real-space) with crystalline reciprocal-space
(pseudo) coordinates.

.. autosummary::

    ~Reflection
    ~ReflectionError
    ~ReflectionsDict
"""

# TODO: refactor how to order the reflections

import logging

from . import Hklpy2Error
from . import SolverBase
from .misc import check_value_in_list
from .misc import unique_name

logger = logging.getLogger(__name__)


class ReflectionError(Hklpy2Error):
    """Custom exceptions from the :mod:`hklpy2.reflection` module."""


class Reflection:
    """
    Coordinates real and pseudo axes.

    .. note:: It is expected this internal routine is called
       from a :class:`~hklpy2.ops.SolverOperator` method,
       not directly by the user.

    .. rubric:: Parameters

    * ``solver`` (:class:`~hklpy2.backends.base.SolverBase`): Backend |solver|.
    * ``pseudos`` (dict): dictionary of pseudo-space axes and values.
    * ``reals`` (dict): dictionary of real-space axes and values.
    * ``wavelength`` (float): Wavelength (:math:`\\lambda`) of incident
      radiation.
    * ``name`` (str): Reference name for this reflection.  If ``None``,
      a random name will be assigned.

    EXAMPLE::

        import hklpy2
        r100 = hklpy2.Reflection(
            solver,
            dict(h=1, k=0, l=0),
            dict(omega=10, chi=0, phi=0, tth=20),
            wavelength=1.00,
            name="r100"
        )

    .. autosummary::

        ~_asdict
        ~name
    """

    # TODO: refactor to remove solver
    # pseudos, reals, wavelength, name, gname, pseudo_names, real_names
    def __init__(
        self, solver, pseudos: dict, reals: dict, wavelength: float, name=None
    ) -> None:
        self.name = name or unique_name()
        self.solver = solver
        self.pseudos = pseudos
        self.reals = reals
        self.wavelength = wavelength
        # Optional items are not part of a "reflection".
        # Such as azimuth, h1, h2, zones, ...

    def _asdict(self):
        """Describe the reflection as a dictionary."""
        return {
            "name": repr(self.name),
            "geometry": repr(self.solver.geometry),
            "pseudos": self.pseudos,
            "reals": self.reals,
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
        """
        Ordered dictionary of diffractometer's reciprocal-space axes.

        Dictionary keys are the axis names, as defined by the diffractometer.
        """
        return self._pseudos

    @pseudos.setter
    def pseudos(self, values):
        if not isinstance(values, dict):
            raise TypeError(f"Must supply dict, received pseudos={values!r}")
        # TODO: Caller should validate.
        for key in values:
            check_value_in_list(
                "Unexpected pseudo axis", key, self.solver.pseudo_axis_names
            )
        for key in self.solver.pseudo_axis_names:
            if key not in values:
                # fmt: off
                raise ReflectionError(
                    f"Missing pseudo axis {key!r}."
                    f" Required names: {self.solver.pseudo_axis_names!r}"
                )
            # fmt: on
        self._pseudos = values

    @property
    def reals(self):
        """
        Ordered dictionary of diffractometer's real-space axes.

        Dictionary keys are the axis names, as defined by the diffractometer.
        """
        return self._reals

    @reals.setter
    def reals(self, values):
        if not isinstance(values, dict):
            raise TypeError(f"Must supply dict, received angles={values!r}")
        # TODO: Caller should validate.
        for key in values:
            check_value_in_list(
                "Unexpected real axis", key, self.solver.real_axis_names
            )
        for key in self.solver.real_axis_names:
            if key not in values:
                # fmt: off
                raise ReflectionError(
                    f"Missing real axis {key!r}."
                    f" Required names: {self.solver.real_axis_names!r}"
                )
            # fmt: on
        self._reals = values

    @property
    def solver(self):
        """Diffractometer |solver|."""
        return self._solver

    @solver.setter
    def solver(self, value):
        if not (isinstance(value, SolverBase) or issubclass(type(value), SolverBase)):
            raise TypeError(f"Must supply SolverBase() object, received solver={value!r}")
        # note: calling SolverBase() will always generate a TypeError
        # "Can't instantiate abstract class SolverBase with abstract methods"
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ordering = []

    def set_orientation_reflections(self, reflections: [Reflection]) -> None:
        """Designate the order of the reflections to be used."""
        self.ordering = [r.name for r in reflections]

    setor = set_orientation_reflections
    """Common alias for :meth:`~set_orientation_reflections`."""

    def add(self, reflection: Reflection, replace: bool = False) -> None:
        """Add an orientation reflection."""
        if reflection.name in self and not replace:
            raise ReflectionError(
                f"Reflection {reflection.name!r} already defined. "
                "Set `replace=True` to replace it."
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

    # ---- get/set properties

    @property
    def ordering(self):
        """List of ordering reflection names."""
        return self._ordering

    @ordering.setter
    def ordering(self, value):
        self._ordering = value
