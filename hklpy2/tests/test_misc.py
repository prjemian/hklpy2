import math
import pathlib
import types
from collections import namedtuple
from contextlib import nullcontext as does_not_raise
from typing import Union

import databroker
import numpy
import pint
import pytest
from bluesky import RunEngine
from bluesky import plans as bp
from ophyd import Component
from ophyd import Device
from ophyd import Signal
from yaml.parser import ParserError

from ..diffract import creator
from ..misc import AnyAxesType
from ..misc import AxesArray
from ..misc import AxesDict
from ..misc import AxesList
from ..misc import AxesTuple
from ..misc import ConfigurationRunWrapper
from ..misc import SolverError
from ..misc import axes_to_dict
from ..misc import compare_float_dicts
from ..misc import convert_units
from ..misc import dict_device_factory
from ..misc import dynamic_import
from ..misc import flatten_lists
from ..misc import get_run_orientation
from ..misc import get_solver
from ..misc import istype
from ..misc import list_orientation_runs
from ..misc import load_yaml_file
from ..misc import roundoff
from ..tests.common import HKLPY2_DIR
from ..tests.common import assert_context_result

sim4c = creator(name="sim4c")
sim6c = creator(name="sim6c", geometry="E6C")
signal = Signal(name="signal", value=1.234)


@pytest.fixture
def cat():
    return databroker.temp().v2


@pytest.fixture
def RE(cat):
    engine = RunEngine({})
    engine.subscribe(cat.v1.insert)
    return engine


@pytest.mark.filterwarnings("error")
@pytest.mark.parametrize(
    "input, names, context, expected",
    [
        [
            [0, 0, 0],
            "h k l",
            pytest.raises(TypeError),
            "Expected a list of names",
        ],
        [
            [0, 0, 0],
            [0, 0, 0],
            pytest.raises(TypeError),
            "Each name should be text,",
        ],
        [dict(h=0, k=0, l=0), "h k l".split(), does_not_raise(), None],
        [
            dict(a=0, k=0, l=0),
            "h k l".split(),
            pytest.raises(KeyError),
            "Missing axis 'h'",
        ],
        [
            namedtuple("PseudoTuple", "h k l".split())(0, 0, 0),
            "h k l".split(),
            does_not_raise(),
            None,
        ],
        ["123", "h k l".split(), pytest.raises(TypeError), "Unexpected type"],
        [
            (1, 2),
            "h k l".split(),
            pytest.raises(ValueError),
            "Expected at least 3 axes, received 2",
        ],
        [
            (1, 2, 3, 4),
            "h k l".split(),
            pytest.raises(UserWarning),
            " Extra inputs will be ignored. Expected 3.",
        ],
        [[0, 1, -1], "aa bb cc".split(), does_not_raise(), None],
        [
            [1.1, 2.2, 3.3, 4, 5],
            "able baker charlie delta echo".split(),
            does_not_raise(),
            None,
        ],
        [
            [1.1, 2.2, 3.3, 4, "text"],
            "able baker charlie delta echo".split(),
            pytest.raises(TypeError),
            "Expected a number. Received: 'text'",
        ],
        [
            "1 2 3".split(),
            "h k l".split(),
            pytest.raises(TypeError),
            "Expected 'AnyAxesType'.",
        ],
    ],
)
def test_axes_to_dict(input, names, context, expected):
    with context as reason:
        axes = axes_to_dict(input, names)
        assert isinstance(axes, dict)
        for name in names:
            assert isinstance(axes.get(name), (float, int))

    assert_context_result(expected, reason)


@pytest.mark.parametrize(
    "a1, a2, tol, equal, context, expected",
    [
        [{}, {}, 0.1, True, does_not_raise(), None],
        [{"a": 0.1}, {"a": 0.1}, 0.1, True, does_not_raise(), None],
        [{"a": 0.1}, {"a": 1.1}, 0.1, False, does_not_raise(), None],
        [{"a": 0.1}, {"b": 0.1}, 0.1, False, does_not_raise(), None],
        [{"a": 0.1}, {}, 0.1, False, does_not_raise(), None],
        [{}, {}, -0.1, False, pytest.raises(ValueError), "should be tol >0"],
        [{"a": 0.11}, {"a": 0.12}, 1, True, does_not_raise(), None],
        [{"a": 0.11}, {"a": 0.12}, 2, False, does_not_raise(), None],
    ],
)
def test_compare_float_dicts(a1, a2, tol, equal, context, expected):
    with context as reason:
        assert compare_float_dicts(a1, a2, tol=tol) == equal

    assert_context_result(expected, reason)


@pytest.mark.parametrize(
    "data, context, expected",
    [
        [{"aa": 1, "bb": "two"}, does_not_raise(), None],
        [1, pytest.raises(AttributeError), "object has no attribute 'items'"],
        [[1], pytest.raises(AttributeError), "object has no attribute 'items'"],
    ],
)
def test_dict_device_factory(data, context, expected):
    with context as reason:
        device_class = dict_device_factory(data)
        assert issubclass(device_class, Device)
        assert device_class.__class__.__name__ == "type"
        assert "DictionaryDevice" in str(device_class)
        for k, v in data.items():
            signal = getattr(device_class, k, None)
            assert signal is not None, f"{v=}"
            assert isinstance(signal, Component), f"{signal=}"
            # assert signal.get() == v

        device = device_class(name="device")
        assert isinstance(device, Device)
        assert device.__class__.__name__ == "DictionaryDevice"
        assert "DictionaryDevice" in str(device)
        for k, v in data.items():
            signal = getattr(device, k, None)
            assert signal is not None, f"{v=}"
            assert isinstance(signal, Signal), f"{signal=}"
            assert signal.get() == v

    assert_context_result(expected, reason)


@pytest.mark.parametrize(
    "source, context, expected, answer",
    [
        [[[1], [2, 3, 4]], does_not_raise(), None, [1, 2, 3, 4]],
        [[[1, 2], [3, 4]], does_not_raise(), None, [1, 2, 3, 4]],
        [[1, 2, 3, 4], does_not_raise(), None, [1, 2, 3, 4]],
        [[], does_not_raise(), None, []],
        [1, pytest.raises(TypeError), "object is not iterable", 1],
    ],
)
def test_flatten_lists(source, context, expected, answer):
    with context as reason:
        result = flatten_lists(source)
        assert isinstance(result, types.GeneratorType)

        result = list(result)
        assert result == answer, f"{source=} {answer=} {result=}"

    assert_context_result(expected, reason)


@pytest.mark.parametrize(
    "solver_name, context, expected",
    [
        ["hkl_soleil", does_not_raise(), None],
        ["no_op", does_not_raise(), None],
        ["th_tth", does_not_raise(), None],
        ["no_such_thing", pytest.raises(SolverError), "unknown.  Pick one of:"],
    ],
)
def test_get_solver(solver_name, context, expected):
    with context as reason:
        solver = get_solver(solver_name)

    assert_context_result(expected, reason)

    if expected is None:
        assert solver is not None


@pytest.mark.parametrize(
    "path, context, expected, keys",
    [
        [
            # YAML file with expected content
            HKLPY2_DIR / "tests" / "e4cv_orient.yml",
            does_not_raise(),
            None,
            ["_header", "name"],
        ],
        [
            # file does not exist (wrong directory)
            HKLPY2_DIR / "e4cv_orient.yml",
            pytest.raises(FileExistsError),
            "YAML file ",
            None,
        ],
        [
            # Not a YAML file, empty
            HKLPY2_DIR / "__init__.py",
            pytest.raises(ParserError),
            "<scalar>",
            None,
        ],
        [
            # Not a YAML file, not empty
            HKLPY2_DIR / "diffract.py",
            pytest.raises(ParserError),
            "expected '<document start>', but found",
            None,
        ],
    ],
)
def test_load_yaml_file(path, context, expected, keys):
    assert isinstance(path, (pathlib.Path, str))
    with context as reason:
        contents = load_yaml_file(path)

    assert_context_result(expected, reason)

    if expected is None:
        # test keys
        not_found = object()
        for key in keys:
            assert contents.get(key, not_found) != not_found, f"{key=}"


@pytest.mark.parametrize(
    "value, digits, expected_text",
    [
        [0, None, "0"],
        [0.123456, None, "0"],
        [0.123456, 4, "0.1235"],
        [-0, 4, "0"],
        [123456, 4, "123456"],
        [123456, -4, "120000"],
        [1.23456e-10, 4, "0"],
        [1.23456e-10, 12, "1.23e-10"],
    ],
)
def test_roundoff(value, digits, expected_text):
    result = roundoff(value, digits)
    assert str(result) == expected_text


@pytest.mark.parametrize(
    "devices, context, expected",
    [
        [[sim4c], does_not_raise(), None],
        [[sim4c.chi], pytest.raises(TypeError), "SoftPositioner"],
        [[sim4c, sim6c], does_not_raise(), None],
        [[sim4c, sim6c.h], pytest.raises(TypeError), "Hklpy2PseudoAxis"],
    ],
)
@pytest.mark.parametrize("enabled", [True, False])
def test_ConfigurationRunWrapper(devices, context, expected, enabled):
    with context as reason:
        crw = ConfigurationRunWrapper(*devices)
        for dev in devices:
            assert dev in crw.devices

        crw.enable = enabled
        assert crw.enable == enabled

        documents = []

        def collector(key, doc):
            nonlocal documents
            documents.append((key, doc))

        assert len(documents) == 0

        RE = RunEngine()
        RE.preprocessors.append(crw.wrapper)
        RE(bp.count([signal]), collector)
        assert len(documents) >= 4

        for key, doc in documents:
            if key == "start":
                configs = doc.get(crw.start_key)
                if enabled:
                    assert configs is not None
                    assert signal.name not in configs
                    for name in crw.device_names:
                        assert name in configs
                    for dev in devices:
                        with does_not_raise() as message:
                            # Try to restore the configuration
                            dev.configuration = configs[dev.name]
                        assert message is None, f"{dev.name=!r} {configs[dev.name]=}"
                else:
                    assert configs is None

    assert_context_result(expected, reason)


@pytest.mark.parametrize("devices", [[], [sim4c], [sim4c, sim6c], [sim6c]])
def test_list_orientation_runs(devices, cat, RE):
    det = signal
    device_names = [d.name for d in devices]
    crw = ConfigurationRunWrapper(*devices)  # TODO: #34 decorator
    RE.preprocessors.append(crw.wrapper)

    def scans():
        yield from bp.count([det])
        yield from bp.count([sim4c])
        yield from bp.count([sim6c])
        yield from bp.count([sim4c, sim6c])

    uids = RE(scans())
    scan_ids = [cat[uid].metadata["start"]["scan_id"] for uid in uids]
    assert scan_ids == [1, 2, 3, 4]

    scan_id = scan_ids[0]
    assert scan_id == 1

    # test get_run_orientation() for specific diffractometer
    info = get_run_orientation(cat[1], name="sim4c")
    assert isinstance(info, dict)
    if sim4c in devices:
        assert len(info) > 0
        assert "_header" in info
    else:
        assert len(info) == 0

    runs = list_orientation_runs(cat)
    assert len(runs) == 4 * len(devices), f"{runs=!r}"
    if len(devices) > 0:
        assert scan_id in runs.scan_id.to_list(), f"{runs=!r}"

    runs = runs.T.to_dict()  # simpler to test as dict structure.
    assert len(runs) == 4 * len(devices), f"{runs=!r}"

    for row in runs.values():
        assert row["scan_id"] in scan_ids
        assert row["diffractometer"] in device_names


@pytest.mark.parametrize(
    "value, annotation, context, expected",
    [
        [{"h": 1.2, "k": 1, "l": -1}, AxesDict, does_not_raise(), None],
        [
            namedtuple("Position", "a b c d".split())(1, 2, 3, 4),
            AxesTuple,
            does_not_raise(),
            None,
        ],
        [[1, 2, 3], AxesList, does_not_raise(), None],
        [(1, 2, 3), AxesTuple, does_not_raise(), None],
        [numpy.array((1, 2, 3, 4, 5)), AxesArray, does_not_raise(), None],
        [{"h": 1.2, "k": 1, "l": -1}, AnyAxesType, does_not_raise(), None],
        [
            namedtuple("Position", "a b c d".split())(1, 2, 3, 4),
            AnyAxesType,
            does_not_raise(),
            None,
        ],
        [[1, 2, 3], AnyAxesType, does_not_raise(), None],
        [(1, 2, 3), AnyAxesType, does_not_raise(), None],
        [numpy.array((1, 2, 3, 4, 5)), AnyAxesType, does_not_raise(), None],
        [None, Union[AnyAxesType, None], does_not_raise(), None],
        [None, AnyAxesType, pytest.raises(AssertionError), "False"],
        [1.234, AnyAxesType, pytest.raises(AssertionError), "False"],
        ["text", AnyAxesType, pytest.raises(AssertionError), "False"],
        [sim4c, AnyAxesType, pytest.raises(AssertionError), "False"],
    ],
)
def test_axes_type_annotations(value, annotation, context, expected):
    with context as reason:
        assert istype(value, annotation)

    assert_context_result(expected, reason)


@pytest.mark.parametrize(
    "name, context, expected",
    [
        ["ophyd.EpicsMotor", does_not_raise(), None],
        ["hklpy2.diffract.creator", does_not_raise(), None],
        [
            "hklpy2.diffract.does_not_exist",
            pytest.raises(AttributeError),
            "has no attribute 'does_not_exist'",
        ],
        [
            "does.not.exist",
            pytest.raises(ModuleNotFoundError),
            "No module named 'does'",
        ],
        ["LocalName", pytest.raises(ValueError), "Must use a dotted path"],
        [
            ".test_utils.CATALOG",
            pytest.raises(ValueError),
            "Must use absolute path, no relative imports",
        ],
    ],
)
def test_dynamic_import(name, context, expected):
    with context as reason:
        dynamic_import(name)

    assert_context_result(expected, reason)


@pytest.mark.parametrize(
    "value, units1, units2, ref, context, expected",
    [
        [32, "fahrenheit", "celsius", 0, does_not_raise(), None],
        [100, "pm", "angstrom", 1, does_not_raise(), None],
        [0.1, "nm", "angstrom", 1, does_not_raise(), None],
        [12400, "eV", "keV", 12.4, does_not_raise(), None],
        [0.1, "nm", "banana", 1, pytest.raises(pint.UndefinedUnitError), "'banana'"],
    ],
)
def test_convert_units(value, units1, units2, ref, context, expected):
    with context as reason:
        assert math.isclose(convert_units(value, units1, units2), ref, abs_tol=0.01)

    assert_context_result(expected, reason)
