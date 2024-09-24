import math
import pathlib

import pytest
import yaml

from ... import SimulatedE4CV
from ...__init__ import __version__
from ..configure import Configuration

e4cv = SimulatedE4CV(name="e4cv")
e4cv is not None

# configuration from hklpy package
e4cv.add_sample("vibranium", 2 * math.pi, digits=3, replace=True)
e4cv.wavelength.put(1.54)
r400 = e4cv.add_reflection((4, 0, 0), (-145.451, 0, 0, 69.066), name="r400")
r040 = e4cv.add_reflection((0, 4, 0), (-145.451, 0, 90, 69.066), name="r040")
r004 = e4cv.add_reflection((0, 0, 4), (-145.451, 90, 0, 69.066), name="r004")
e4cv.operator.calcUB(r040, r004)


@pytest.mark.parametrize(
    "keypath, value",
    [
        ["_header.datetime", None],
        ["_header.energy_units", e4cv._wavelength.energy_units],
        ["_header.energy", e4cv._wavelength.energy],
        ["_header.hklpy2_version", __version__],
        ["_header.python_class", e4cv.__class__.__name__],
        ["_header.source_type", e4cv._wavelength.source_type],
        ["_header.wavelength_units", e4cv._wavelength.wavelength_units],
        ["_header.wavelength", e4cv._wavelength.wavelength],
        ["axes.axes_xref", e4cv.operator.axes_xref],
        ["axes.extra_axes", e4cv.operator.solver.extras],
        ["axes.pseudo_axes", e4cv.pseudo_axis_names],
        ["axes.real_axes", e4cv.real_axis_names],
        ["constraints.chi.high_limit", 180],
        ["constraints.omega.label", "omega"],
        ["constraints.tth.low_limit", -180],
        ["geometry", e4cv.operator.solver.geometry],
        ["name", e4cv.name],
        ["sample_name", e4cv.operator.sample.name],
        ["samples.sample.lattice.a", 1],
        ["samples.sample.lattice.alpha", 90],
        ["samples.sample.name", "sample"],
        ["samples.sample.reflections", {}],
        ["samples.sample.U", [[1, 0, 0], [0, 1, 0], [0, 0, 1]]],
        ["samples.sample.UB", [[1, 0, 0], [0, 1, 0], [0, 0, 1]]],
        ["samples.vibranium.name", "vibranium"],
        ["samples.vibranium.reflections.r004.name", "r004"],
        ["samples.vibranium.reflections.r004.order", 1],
        ["samples.vibranium.reflections.r004.pseudos.h", 0],
        ["samples.vibranium.reflections.r004.pseudos.k", 0],
        ["samples.vibranium.reflections.r004.pseudos.l", 4],
        ["samples.vibranium.reflections.r004.reals.chi", 90],
        ["samples.vibranium.reflections.r400.order", "unused"],
        ["samples.vibranium.U", e4cv.operator.solver.U],
        ["samples.vibranium.UB", e4cv.operator.solver.UB],
        ["solver.engine", e4cv.operator.solver.engine_name],
        ["solver.mode", e4cv.operator.solver.mode],
        ["solver.name", e4cv.operator.solver.name],
        ["solver.real_axes", e4cv.operator.solver.real_axis_names],
    ],
)
def test_Configuration(keypath, value):
    config = Configuration(e4cv)._asdict()
    assert "_header" in config, f"{config=!r}"
    assert "file" not in config["_header"], f"{config=!r}"

    for k in keypath.split("."):
        config = config.get(k)  # narrow the search
        assert config is not None, f"{k=!r}  {keypath=!r}"

    if value is not None:
        assert value == config, f"{k=!r}  {value=!r}  {config=!r}"


def test_Configuration_export(tmp_path):
    assert isinstance(tmp_path, pathlib.Path)
    assert tmp_path.exists()

    config_file = tmp_path / "config.yml"
    assert not config_file.exists()

    # write the YAML file
    config = Configuration(e4cv)
    config.export(config_file)
    assert config_file.exists()

    # read the YAML file, check for _header.file key
    saved_config = yaml.load(open(config_file, "r").read(), yaml.Loader)
    assert "_header" in saved_config, f"{saved_config=!r}"
    assert "file" in saved_config["_header"], f"{saved_config=!r}"
