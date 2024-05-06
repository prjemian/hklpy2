"""
Coordinates of a crystalline reflection.

Associates diffractometer angles (real-space) with crystalline reciprocal-space
(pseudo) coordinates.

.. autosummary::

    ~Reflection

.. caution:: Development continues.  This API will change.
"""

import uuid


class Reflection:
    """Coordinates real and pseudo axes."""

    def __init__(self, geo, angles, pseudos, wavelength, name=None) -> None:
        self.name = name or str(uuid.uuid4())[:7]
        self.geometry = geo
        # TODO: internally, should be dicts
        self.angles = angles  # TODO: could be provided as dict, tuple, or list
        self.pseudos = pseudos  # TODO: could be dict, tuple, or list
        self.wavelength = wavelength  # TODO: could be optional

    def _asdict(self):
        """Describe the reflection as a dictionary."""
        return {
            "name": self.name,
            "angles": self.angles,
            "pseudos": self.pseudos,
            "wavelength": self.wavelength,
            "geometry": self.gname,
        }

    def __repr__(self):
        """
        Standard representation of reflection.
        """
        parameters = [f"{k}={v}" for k, v in self._asdict().items()]
        # TODO: check that details are rendered
        return "Reflection(" + ", ".join(parameters) + ")"
