"""
Base class for all diffractometers

.. autosummary::

    ~DiffractometerBase
"""

import logging

from ophyd import Component as Cpt
from ophyd import PseudoPositioner
from ophyd.pseudopos import pseudo_position_argument
from ophyd.pseudopos import real_position_argument
from ophyd.signal import AttributeSignal

from . import Hklpy2Error

# from .misc import check_value_in_list
# from .misc import get_solver
# from .misc import solver_factory
# from .misc import solvers
from .wavelength_support import DEFAULT_WAVELENGTH
from .wavelength_support import ConstantMonochromaticWavelength

__all__ = ["DiffractometerBase"]
logger = logging.getLogger(__name__)

DEFAULT_PHOTON_ENERGY_KEV = 8.0


class DiffractometerError(Hklpy2Error):
    """Custom exceptions from a :class:`~DiffractometerBase` subclass."""


class DiffractometerBase(PseudoPositioner):
    """
    Base class for all diffractometers.

    .. rubric:: (ophyd) Components

    .. rubric :: (ophyd) Attribute Components

    .. autosummary::

        ~wavelength
        ~wavelength_units

    .. rubric:: Python Methods

    .. autosummary::

        ~forward
        ~inverse

    .. rubric:: Python Properties
    """

    # TODO: allow for extra pseudos and reals
    # Allow the subclass to provide more axes than required.
    # Also allow axes to be renamed.
    # Needs a way to specify which ones used with particular solver.

    # These two attributes are used by the PseudoPositioner class.
    # _pseudo = []  # List of pseudo-space PseudoPositioner objects.
    # _real = []  # List of real-space positioner objects.

    # TODO: need a solver object AND a solver name
    solver = Cpt(
        AttributeSignal,
        attr="solver_name",
        doc="Name of backend |solver| (library).",
        write_access=True,
    )
    """Name of backend |solver| (library)."""

    geometry = Cpt(
        AttributeSignal,
        attr="geometry_name",
        doc="Name of backend |solver| geometry.",
        write_access=True,
    )
    """Name of backend |solver| geometry."""

    wavelength = Cpt(
        AttributeSignal,
        attr="_wavelength.wavelength",
        doc="incident wavelength, (angstrom)",
        write_access=False,
    )
    """Incident wavelength."""

    wavelength_units = Cpt(
        AttributeSignal,
        attr="_wavelength.wavelength_units",
        doc="engineering units of the incident wavelength",
        write_access=False,
    )
    """Engineering units of the incident wavelength."""

    def __init__(
        self,
        *args,
        # solver: str = "",
        # geometry: str = "",
        # engine: str = "",
        **kwargs,
    ):
        # self.solver_name = solver
        # self.geometry_name = geometry
        self._wavelength = ConstantMonochromaticWavelength(DEFAULT_WAVELENGTH)

        super().__init__(*args, **kwargs)

    @pseudo_position_argument
    def forward(self, pseudos: dict):
        """Compute tuple of reals from pseudos (hkl -> angles)."""
        # TODO: have the solver handle this, from the pseudos
        print(f"forward(): {pseudos=!r}")
        pos = {axis[0]: 0 for axis in self._get_real_positioners()}
        return self.RealPosition(**pos)

    @real_position_argument
    def inverse(self, reals: dict):
        """Compute tuple of pseudos from reals (angles -> hkl)."""
        # TODO: have the solver handle this, from the reals
        print(f"inverse(): {reals=!r}")
        pos = {axis[0]: 0 for axis in self._get_pseudo_positioners()}
        return self.PseudoPosition(**pos)

    # ---- get/set properties

    # @property
    # def engine_name(self):
    #     """Backend |solver| geometry name."""
    #     return self._engine_name

    # @engine_name.setter
    # def engine_name(self, value: str):
    #     if self.solver_name != "" and self.geometry_name != "":
    #         solver = solver_factory(self.solver_name, geometry=self.geometry_name)
    #         check_value_in_list("Engine", value, list(solver.engines()))
    #     self._engine_name = value

    # @property
    # def geometry_name(self):
    #     """Backend |solver| geometry name."""
    #     return self._geometry_name

    # @geometry_name.setter
    # def geometry_name(self, value: str):
    #     if self.solver_name != "":
    #         sclass = get_solver(self.solver_name)
    #         check_value_in_list("Geometry", value, list(sclass.geometries()))
    #     self._geometry_name = value

    # @property
    # def solver_name(self):
    #     """Backend |solver| library name."""
    #     return self._solver_name

    # @solver_name.setter
    # def solver_name(self, value: str):
    #     check_value_in_list("Solver", value, list(solvers()), blank_ok=True)
    #     self._solver_name = value
