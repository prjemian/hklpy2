"""
Supports export and restore diffractometer configurations.

.. autosummary::

    ~Configuration

From **hklpy**, these TODO items:

- bluesky runs support
- stack support
- set constraints

.. seealso:: # https://pyyaml.org/wiki/PyYAMLDocumentation
"""

import logging

from .misc import ConfigurationError

logger = logging.getLogger(__name__)


class Configuration:
    """
    Manage diffractometer configurations.

    .. autosummary::

        ~_asdict
        ~_fromdict
        ~_valid
    """

    def __init__(self, diffractometer) -> None:
        self.diffractometer = diffractometer

    def _asdict(self) -> dict:
        """Return diffractometer's configuration as a dict."""
        return self.diffractometer.operator._asdict()

    def _fromdict(
        self,
        config: dict,
        clear: bool = True,
        restore_constraints: bool = True,
    ):
        """Restore diffractometer's configuration from a dict."""
        self._valid(config)  # will raise if invalid

        if clear:
            self.diffractometer.operator.reset_constraints()
            self.diffractometer.operator.reset_samples()

        if restore_constraints:
            controls = {}
            oper = self.diffractometer.operator  # alias
            for axis, v in config["constraints"].items():
                axis_canonical = config["axes"]["axes_xref"][axis]
                axis_local = oper.axes_xref_reversed[axis_canonical]
                v["label"] = axis_local  # must match
                controls[axis_local] = v
            config["constraints"] = controls
        else:
            config["constraints"] = {}

        self.diffractometer.operator._fromdict(config)

    def _valid(self, config):
        """Validate incoming configuration for current diffractometer."""

        def compare(incoming, existing, template):
            if incoming != existing:
                message = template % (incoming, existing)
                raise ConfigurationError(message)
                # logger.warning(template, incoming, existing)
                # return False

        compare(
            config.get("solver", {}).get("name"),
            self.diffractometer.operator.solver.name,
            "solver mismatch: incoming=%r existing=%r",
        )
        if "engine" in dir(self.diffractometer.operator.solver):
            compare(
                config.get("solver", {}).get("engine"),
                self.diffractometer.operator.solver.engine_name,
                "engine mismatch: incoming=%r existing=%r",
            )
        compare(
            config.get("solver", {}).get("geometry"),
            self.diffractometer.operator.solver.geometry,
            "geometry mismatch: incoming=%r existing=%r",
        )
        compare(
            config.get("axes", {}).get("pseudo_axes"),
            # ignore any extra pseudos
            self.diffractometer.pseudo_axis_names[
                : len(self.diffractometer.operator.solver.pseudo_axis_names)
            ],
            "pseudo axis mismatch: incoming=%r existing=%r",
        )
        compare(
            config.get("solver", {}).get("real_axes"),
            self.diffractometer.operator.solver.real_axis_names,
            "solver real axis mismatch: incoming=%r existing=%r",
        )
