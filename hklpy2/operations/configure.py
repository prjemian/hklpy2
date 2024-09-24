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

import datetime
import pathlib

import yaml

from ..__init__ import __version__


class Configuration:
    """
    Manage diffractometer configurations.

    .. autosummary::

        ~_asdict
        ~export
"""

    def __init__(self, diffractometer) -> None:
        self.diffractometer = diffractometer

    def _asdict(self):
        """Return diffractometer's configuration as a dict."""

        dfrct = self.diffractometer  # local shortcut
        config = {
            "_header": {
                "datetime": str(datetime.datetime.now()),
                "energy_units": dfrct._wavelength.energy_units,
                "energy": dfrct._wavelength.energy,
                "hklpy2_version": __version__,
                "python_class": dfrct.__class__.__name__,
                "source_type": dfrct._wavelength.source_type,
                "wavelength_units": dfrct._wavelength.wavelength_units,
                "wavelength": dfrct._wavelength.wavelength,
            },
        }
        config.update(dfrct.operator._asdict())
        return config

    def export(self, file):
        """Export the diffractometer configuration to a YAML file."""
        path = pathlib.Path(file)
        config = self._asdict()
        config["_header"]["file"] = str(file)
        dump = yaml.dump(
            config,
            indent=2,
            default_flow_style=False,
        )
        with open(path, "w") as y:
            y.write("#hklpy2 configuration file\n\n")
            y.write(dump)
