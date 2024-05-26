import pytest


@pytest.fixture
def sim():
    from ophyd import Component as Cpt
    from ophyd import PseudoSingle
    from ophyd import SoftPositioner

    from ...backends.th_tth_q import TH_TTH_Q_GEOMETRY
    from ...diffract import DiffractometerBase

    class Simulator(DiffractometerBase):
        """Simulate diffractometer to test sample."""

        red = Cpt(PseudoSingle, "")
        blue = Cpt(SoftPositioner, init_pos=0)
        orange = Cpt(SoftPositioner, init_pos=0)

        def __init__(self, *args, **kwargs):
            super().__init__(
                *args,
                solver="th_tth",
                geometry=TH_TTH_Q_GEOMETRY,
                **kwargs,
            )
            self.operator.auto_assign_axes()

    sim = Simulator("", name="sim")
    yield sim
