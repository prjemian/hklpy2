# pylint: disable=too-many-arguments
"""
Coordinates of a crystalline reflection.

Associates diffractometer angles (real-space) with crystalline reciprocal-space
(pseudo) coordinates.

.. autosummary::

    ~Reflection
    ~ReflectionError
    ~ReflectionsDict
    ~UNUSED_REFLECTION
"""

import logging

from .. import Hklpy2Error
from .misc import check_value_in_list
from .misc import compare_float_dicts

logger = logging.getLogger(__name__)

UNUSED_REFLECTION = "unused"
"""Identifies an unused reflection in the ReflectionsList."""


class ReflectionError(Hklpy2Error):
    """Custom exceptions from the :mod:`hklpy2.operations.reflection` module."""


class Reflection:
    """
    Coordinates real and pseudo axes.

    .. note:: Internal use only.

       It is expected this internal routine is called
       from a method of :class:`~hklpy2.ops.Operations`,
       not directly by the user.

    .. rubric:: Parameters

    * ``name`` (str): Reference name for this reflection.
    * ``pseudos`` (dict): Unordered dictionary of pseudo-space axes and values.
    * ``reals`` (dict): Unordered dictionary of real-space axes and values.
    * ``wavelength`` (float): Wavelength of incident radiation.
    * ``geometry`` (str): Geometry name for this reflection.
    * ``pseudo_names`` ([str]): Ordered list of pseudo names for this geometry.
    * ``rnames`` ([str]): Ordered list of real names for this geometry.

    Optional items (such as 'azimuth', 'h1', 'h2', zones, ...) are not
    part of a "reflection".

    .. autosummary::

        ~__eq__
        ~_asdict
        ~_validate_pseudos
        ~_validate_reals
        ~_validate_wavelength
        ~pseudos
        ~reals
        ~wavelength
    """

    def __init__(
        self,
        name: str,
        pseudos: dict,
        reals: dict,
        wavelength: float,
        geometry: str,
        pseudo_axis_names: list,
        real_axis_names: list,
        digits: int = 4,
    ) -> None:
        self.digits = digits
        self.geometry = geometry
        self.name = name
        self.pseudo_axis_names = pseudo_axis_names
        self.real_axis_names = real_axis_names

        # property setters
        self.pseudos = pseudos
        self.reals = reals
        self.wavelength = wavelength

    def _asdict(self):
        """Describe the reflection as a dictionary."""
        return {
            "name": self.name,
            "geometry": self.geometry,
            "pseudos": self.pseudos,
            "reals": self.reals,
            "wavelength": self.wavelength,
        }

    def __repr__(self):
        """
        Standard representation of reflection.
        """
        parameters = []
        for k, v in self._asdict().items():
            if isinstance(v, float):
                v = round(v, self.digits)
            parameters.append(f"{k}={v!r}")
        return "Reflection(" + ", ".join(parameters) + ")"

    def __eq__(self, r2):
        """
        Compare this reflection with another for equality.

        Precision is controlled by rounding to smallest number of digits
        between the reflections.
        """
        digits = min(self.digits, r2.digits)
        return (
            compare_float_dicts(self.pseudos, r2.pseudos, digits)
            and compare_float_dicts(self.reals, r2.reals, digits)
            and round(self.wavelength, digits) == round(r2.wavelength, digits)
        )

    def _validate_pseudos(self, value):
        """Raise Exception if pseudos do not match expectations."""
        if not isinstance(value, dict):
            raise TypeError(f"Must supply dict, received pseudos={value!r}")
        for key in value:
            check_value_in_list("pseudo axis", key, self.pseudo_axis_names)
        for key in self.pseudo_axis_names:
            if key not in value:
                # fmt: off
                raise KeyError(
                    f"Missing pseudo axis {key!r}."
                    f" Required names: {self.pseudo_axis_names!r}"
                )
            # fmt: on

    def _validate_reals(self, value):
        """Raise Exception if reals do not match expectations."""
        if not isinstance(value, dict):
            raise TypeError(f"Must supply dict, received reals={value!r}")
        for key in value:
            check_value_in_list("real axis", key, self.real_axis_names)
        for key in self.real_axis_names:
            if key not in value:
                # fmt: off
                raise KeyError(
                    f"Missing real axis {key!r}."
                    f" Required names: {self.real_axis_names!r}"
                )
            # fmt: on

    def _validate_wavelength(self, value):
        """Raise exception if pseudos do not match expectations."""
        if not isinstance(value, (int, float)):
            raise TypeError(f"Must supply number, received {value=!r}")
        if value <= 0:
            raise ValueError(f"Must be >=0, received {value=}")

    # --------- get/set properties

    @property
    def name(self):
        """Sample name."""
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
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
        self._validate_pseudos(values)
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
        self._validate_reals(values)
        self._reals = values

    @property
    def wavelength(self):
        """Wavelength of reflection."""
        return self._wavelength

    @wavelength.setter
    def wavelength(self, value):
        self._validate_wavelength(value)
        self._wavelength = value


class ReflectionsDict(dict):
    """
    Dictionary of Reflections.

    .. autosummary::

        ~_asdict
        ~_validate_reflection
        ~add
        ~order
        ~prune
        ~set_orientation_reflections
        ~setor
        ~swap
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._order = []
        self.geometry = None

    def __repr__(self):
        """
        Standard representation of reflections list.

        Order numbers start from zero.
        """
        return repr(self._asdict())

    def _asdict(self):
        """
        Describe the reflections list as an ordered dictionary.

        Order by reflections order.
        """
        self.prune()
        result = {}
        # Ordered reflections first, numbers start from zero.
        for i, k in enumerate(self.order):
            refl = self[k]._asdict()
            refl["order"] = i
            result[self[k].name] = refl
        # Then, any unused reflections.
        for k in self.keys():
            if k not in self.order:
                refl = self[k]._asdict()
                refl["order"] = UNUSED_REFLECTION
                result[self[k].name] = refl
        return result

    def set_orientation_reflections(
        self,
        reflections: list[Reflection],
    ) -> None:
        """
        Designate the order of the reflections to be used.

        .. note:: Raises ``KeyError`` if any
           ``reflections`` are not already defined.

           This method does not *add* any new reflections.

        .. rubric:: Parameters

        * ``reflections`` ([Reflection]) : List of
          :class:`hklpy2.operations.reflection.Reflection` objects.
        """
        self.order = [r.name for r in reflections]

    setor = set_orientation_reflections
    """Common alias for :meth:`~set_orientation_reflections`."""

    def add(self, reflection: Reflection, replace: bool = False) -> None:
        """Add a single orientation reflection."""
        self._validate_reflection(reflection, replace)
        self[reflection.name] = reflection
        if reflection.name not in self.order:
            self.order.append(reflection.name)
        self.prune()

    def prune(self):
        """Remove any undefined reflections from order list."""
        self.order = [refl for refl in self.order if refl in self]

    def swap(self):
        """Swap the two named orientation reflections."""
        if len(self.order) < 2:
            raise ReflectionError("Need at least two reflections to swap.")
        rname1, rname2 = self.order[:2]
        self._order[0] = rname2
        self._order[1] = rname1

    def _validate_reflection(self, reflection, replace):
        """Validate the new reflection."""
        if not isinstance(reflection, Reflection):
            raise TypeError(
                f"Unexpected {reflection=!r}.  Must be a 'Reflection' type."
            )
        if reflection.name in self and not replace:
            raise ReflectionError(
                f"Reflection name {reflection.name!r} already defined. "
                "Set `replace=True` to replace it."
            )
        if self.geometry is None or len(self) == 0:
            self.geometry = reflection.geometry
        if reflection.geometry != self.geometry:
            # fmt: off
            raise ValueError(
                "geometry does not match previous reflections:"
                f" received {reflection.geometry!r}"
                f" previous: {self.geometry!r}."
            )
            # fmt: on

        # Compare with all existing reflections for duplicate contents.
        this = reflection._asdict()
        this.pop("name")  # might use a different name
        for v in self.values():
            existing = v._asdict()
            existing.pop("name")
            if compare_float_dicts(this, existing):
                raise ReflectionError(
                    f"Reflection {reflection!r} matches existing {v.name!r}"
                )

    # ---- get/set properties

    @property
    def order(self):
        """Ordered list of reflection names used for orientation."""
        return self._order

    @order.setter
    def order(self, value):
        self._order = list(value)
