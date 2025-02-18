"""
Export and restore diffractometer configurations.

.. autosummary::

    ~Configuration

From **hklpy**, these TODO items:

- bluesky runs support
- stack support
- set constraints

.. seealso:: # https://pyyaml.org/wiki/PyYAMLDocumentation
"""

import logging
import pathlib

import yaml

from .misc import ConfigurationError
from .misc import load_yaml_file

logger = logging.getLogger(__name__)


class Configuration:
    """
    Manage diffractometer configurations.

    .. autosummary::

        ~_asdict
        ~_fromdict
        ~_valid
        ~export
        ~restore
    """

    def __init__(self, diffractometer) -> None:
        self.diffractometer = diffractometer

    def _asdict(self) -> dict:
        """Return diffractometer's configuration as a dict."""
        return self.diffractometer.operator._asdict()

    def export(self, file, comment=""):
        """
        Export the diffractometer configuration to a YAML file.

        Example::

            import hklpy2

            e4cv = hklpy2.diffractometer_factory(name="e4cv")
            e4cv.operator.configuration.export("e4cv-config.yml", comment="example")
        """
        path = pathlib.Path(file)
        config = self.diffractometer.operator._asdict()
        config["_header"]["file"] = str(file)
        config["_header"]["comment"] = str(comment)
        dump = yaml.dump(
            config,
            indent=2,
            default_flow_style=False,
            sort_keys=False,
        )
        with open(path, "w") as y:
            y.write("#hklpy2 configuration file\n\n")
            y.write(dump)

    def restore(self, file, clear=True, restore_constraints=True, solver=None):
        """
        Restore the diffractometer configuration to a YAML file.

        Example::

            import hklpy2

            e4cv = hklpy2.diffractometer_factory(name="e4cv")
            e4cv.operator.configuration.restore("e4cv-config.yml")

        PARAMETERS

        file *str* or *pathlib.Path* object:
            Name (or pathlib object) of diffractometer configuration YAML file.
        clear *bool*:
            If ``True`` (default), remove any previous configuration of the
            diffractometer and reset it to default values before restoring the
            configuration.

            If ``False``, sample reflections will be append with all reflections
            included in the configuration data for that sample.  Existing
            reflections will not be changed.  The user may need to edit the
            list of reflections after ``restore(clear=False)``.
        restore_constraints *bool*:
            If ``True`` (default), restore any constraints provided.

        Note: Can't name this method "import", it's a reserved Python word.
        """
        path = pathlib.Path(file)
        if not path.exists():
            raise FileExistsError(f"{path}")

        config = load_yaml_file(path)
        self._fromdict(config, clear, restore_constraints)

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
            self.diffractometer.pseudo_axis_names,
            "pseudo axis mismatch: incoming=%r existing=%r",
        )
        compare(
            config.get("solver", {}).get("real_axes"),
            self.diffractometer.operator.solver.real_axis_names,
            "solver real axis mismatch: incoming=%r existing=%r",
        )
