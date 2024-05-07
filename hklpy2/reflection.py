"""
Coordinates of a crystalline reflection.

Associates diffractometer angles (real-space) with crystalline reciprocal-space
(pseudo) coordinates.

.. autosummary::

    ~Reflection
"""

import uuid


class Reflection:
    """
    Coordinates real and pseudo axes.

    EXAMPLE::

        import hklpy2
        r1 = hklpy2.Reflection(...)  # TODO
    """

    def __init__(
        self, solver, pseudos: dict, angles: dict, wavelength: float, name=None
    ) -> None:
        self.name = name or str(uuid.uuid4())[:7]
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
