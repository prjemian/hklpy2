from contextlib import nullcontext as does_not_raise

import pytest
from bluesky import RunEngine
from bluesky import plans as bp
from ophyd import Signal

from ... import SimulatedE4CV
from ... import SimulatedE6C
from ..misc import ConfigurationRunWrapper
from ..misc import roundoff

sim4c = SimulatedE4CV(name="sim4c")
sim6c = SimulatedE6C(name="sim6c")
signal = Signal(name="signal", value=1.234)


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
    "devices, outcome, expect",
    [
        [[sim4c], does_not_raise(), None],
        [[sim4c.chi], pytest.raises(TypeError), "SoftPositioner"],
        [[sim4c, sim6c], does_not_raise(), None],
        [[sim4c, sim6c.h], pytest.raises(TypeError), "PseudoSingle"],
    ],
)
@pytest.mark.parametrize("enabled", [True, False])
def test_ConfigurationRunWrapper(devices, outcome, expect, enabled):
    with outcome as excuse:
        crw = ConfigurationRunWrapper(*devices)
        for dev in devices:
            assert dev in crw.devices

        crw.enable = enabled

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

    if expect is not None:
        assert expect in str(excuse), f"{excuse=} {expect=}"
