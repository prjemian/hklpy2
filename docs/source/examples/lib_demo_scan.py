"""
WIP: Library for demo_scan_hkl_hklpy2 notebook.  Hoist into hklpy2, somehow.
"""

__all__ = ["scan_extra_parameter"]

from itertools import islice

import numpy
from bluesky import plan_stubs as bps
from bluesky import preprocessors as bpp
from hklpy2 import DiffractometerBase
from hklpy2 import SolverError
from ophyd import Signal


class DocCollector:
    """RE callback to collect all documents from the bluesky RunEngine."""

    def __init__(self):
        self.documents = []

    def receiver(self, key, doc):
        self.documents.append((key, doc))


collector = DocCollector()


def chunk(it, size):
    """Return tuples of 'size' from list 'it'."""
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


def scan_extra_parameter(
    dfrct: object = None,
    detectors: list = [],
    axis: str = None,  # name of extra parameter to be scanned
    start: float = None,
    finish: float = None,
    num: int = None,
    pseudos: dict = None,
    reals: dict = None,
    extras: dict = {},  # define all but the 'axis', these will remain constant
    md: dict = None,
):
    """
    Scan one (or more) extra diffractometer parameter(s).

    Such as psi

    - iterate extras as decribed:
    - set extras
    - solution = forward(pseudos)
    - move to solution
    - trigger detectors
    - read all controls
    """
    # if pseudos is None and reals is None:
    #     raise SolverError("Must define either pseudos or reals.")
    # if pseudos is not None and reals is not None:
    #     raise SolverError("Cannot define both pseudos and reals.")
    forwardTransformation = reals is None

    _md = {
        "diffractometer": {
            "name": dfrct.name,
            "solver": dfrct.operator.solver.name,
            "geometry": dfrct.operator.solver.geometry,
            "engine": dfrct.operator.solver.engine_name,
            "mode": dfrct.operator.solver.mode,
            "extra_axes": dfrct.operator.solver.extra_axis_names,
        },
        "axis": axis,
        "start": start,
        "finish": finish,
        "num": num,
        "pseudos": pseudos,
        "reals": reals,
        "extras": extras,
        "transformation": "forward" if forwardTransformation else "inverse",
    }
    _md.update(md or {})

    signal = Signal(name=axis, value=start)
    controls = detectors
    controls.append(dfrct)
    controls.append(signal)
    # TODO: controls.append(extras_device)  # TODO: need Device to report ALL extras
    controls = list(set(controls))

    @bpp.stage_decorator(detectors)
    @bpp.run_decorator(md=_md)
    def _inner():
        dfrct.operator.solver.extras = extras
        for value in numpy.linspace(start, finish, num=num):
            yield from bps.mv(signal, value)

            dfrct.operator.solver.extras = {axis: value}  # just the changing one
            if forwardTransformation:
                solution = dfrct.forward(pseudos)
                # TODO: Could provide a test run without the moves.
                reals = []  # convert to ophyd real positioner objects
                for k, v in solution._asdict().items():
                    reals.append(getattr(dfrct, k))
                    reals.append(v)
                yield from bps.mv(*reals)
            else:
                pass  # TODO: inverse

            # yield from bps.trigger(detectors)
            yield from bps.create("primary")
            for item in controls:
                yield from bps.read(item)
            yield from bps.save()

    return (yield from _inner())


def again(
    dfrct: DiffractometerBase,
    detectors: list,
    *args: tuple,
    num: int = None,
    pseudos: dict = None,
    reals: dict = None,
    extras: dict = {},  # define all but the 'axis', these will remain constant
    md: dict = None,
):
    # validations
    if not isinstance(dfrct, DiffractometerBase):
        raise ValueError(f"'dfrct' must be a hklpy2 Diffractometer. Received {dfrct!r}")
    if num is None:
        if len(args) % 3 != 1:
            raise ValueError(
                "The number of points to scan must be provided "
                "as the last positional argument or as keyword "
                "argument 'num'."
            )
        num = args[-1]
        args = args[:-1]

    if not (float(num).is_integer() and num > 0.0):
        raise ValueError(
            f"The parameter `num` is expected to be a number of "
            f"steps (not step size!) It must therefore be a "
            f"whole number. The given value was {num}."
        )

    if len(args) % 3 != 0:
        raise ValueError(
            "The list of arguments must contain groups of"
            " extra_parameter_name, start_position, finish_position,"
        )
    num = int(num)

    if pseudos is None and reals is None:
        raise SolverError("Must define either pseudos or reals.")
    if None not in [pseudos, reals]:
        raise SolverError("Cannot define both pseudos and reals.")

    scan_parms = list(chunk(args, 3))  # name, start, finish
    # TODO validate that all names are in extras

    # assignments
    forwardTransformation = reals is None
    signals = [Signal(name=k, value=start) for k, start, _ in scan_parms]
    series = {
        k: numpy.linspace(start, finish, num=num) for k, start, finish in scan_parms
    }
    controls = list(set(detectors + [dfrct] + signals))

    _md = {}
    _md.update(md or {})

    @bpp.stage_decorator(detectors)
    @bpp.run_decorator(md=_md)
    def _inner():
        dfrct.operator.solver.extras = extras
        for n in range(num):
            yield from bps.checkpoint()

            # set iterated extras
            for signal in signals:
                yield from bps.mv(signal, series[signal.name][n])
                dfrct.operator.solver.extras = {signal.name: signal.get()}

            if forwardTransformation:
                solution = dfrct.forward(pseudos)
                # TODO: Could provide a test run without the moves.
                reals = []  # convert to ophyd real positioner objects
                for k, v in solution._asdict().items():
                    reals.append(getattr(dfrct, k))
                    reals.append(v)
                yield from bps.mv(*reals)
            else:
                solution = dfrct.inverse(reals)
                for k, v in solution._asdict().items():
                    pseudos.append(getattr(dfrct, k))
                    pseudos.append(v)
                yield from bps.mv(*pseudos)

            yield from bps.trigger(detectors)
            yield from bps.create("primary")
            for item in controls:
                yield from bps.read(item)
            yield from bps.save()

    # return (yield from _inner())


# if __name__ == "__main__":
#     from hklpy2 import SimulatedE4CV
#     from ophyd.sim import noisy_det

#     e4cv = SimulatedE4CV(name="e4cv")
#     again(
#         e4cv,
#         [noisy_det],
#         # fmt: off
#         "psi", 1, 5,
#         # fmt: on
#         12,
#         pseudos=(1, 0, 1),
#         extras=dict(h2=1, k2=0, l2=0),
#     )
