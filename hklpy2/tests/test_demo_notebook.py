from math import pi

import hklpy2
import pytest


@pytest.fixture
def fourc():
    from ophyd import Component as Cpt
    from ophyd import Kind
    from ophyd import PseudoSingle
    from ophyd import SoftPositioner

    NORMAL_HINTED = Kind.hinted | Kind.normal

    class Fourc(hklpy2.DiffractometerBase):
        """Test case."""

        # pseudo-space axes, in order expected by hkl_soleil E4CV, engine="hkl"
        h = Cpt(PseudoSingle, "", kind=NORMAL_HINTED)  # noqa: E741
        k = Cpt(PseudoSingle, "", kind=NORMAL_HINTED)  # noqa: E741
        l = Cpt(PseudoSingle, "", kind=NORMAL_HINTED)  # noqa: E741

        # real-space axes, in order expected by hkl_soleil E4CV
        # using different names
        theta = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=NORMAL_HINTED)
        chi = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=NORMAL_HINTED)
        phi = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind=NORMAL_HINTED)
        ttheta = Cpt(SoftPositioner, limits=(-170, 170), init_pos=0, kind=NORMAL_HINTED)

        # pseudo-space extra axes used in a couple modes
        h2 = Cpt(PseudoSingle, "", kind=NORMAL_HINTED)  # noqa: E741
        k2 = Cpt(PseudoSingle, "", kind=NORMAL_HINTED)  # noqa: E741
        l2 = Cpt(PseudoSingle, "", kind=NORMAL_HINTED)  # noqa: E741

        # real-space extra axis used in a couple modes
        psi = Cpt(SoftPositioner, limits=(-170, 170), init_pos=0, kind=NORMAL_HINTED)

        # another Component, not used (yet)
        energy = Cpt(SoftPositioner, limits=(5, 35), init_pos=12.4, kind=NORMAL_HINTED)

        def __init__(self, *args, **kwargs):
            super().__init__(
                *args,
                solver="hkl_soleil",
                geometry="E4CV",
                solver_kwargs={"engine": "hkl"},
                **kwargs,
            )
            self.operator.auto_assign_axes()

    fourc = Fourc("", name="fourc")
    yield fourc


def test_as_in_demo_notebook(fourc):
    assert "E4CV" in fourc.operator.solver.geometries()
    assert fourc.solver.get() == "hkl_soleil"
    assert fourc.geometry.get() == "E4CV"
    assert fourc.wavelength.get() == 1.0
    assert fourc.operator.axes_xref == {
        "h": "h",
        "k": "k",
        "l": "l",
        "theta": "omega",
        "chi": "chi",
        "phi": "phi",
        "ttheta": "tth",
    }

    assert fourc.pseudo_axis_names == ["h", "k", "l", "h2", "k2", "l2"]
    assert fourc.real_axis_names == ["theta", "chi", "phi", "ttheta", "psi", "energy"]
    assert fourc.operator.solver.pseudo_axis_names == ["h", "k", "l"]
    assert fourc.operator.solver.real_axis_names == ["omega", "chi", "phi", "tth"]
    assert fourc.operator.solver.extra_axis_names == []

    expected = "{'position': FourcPseudoPos(h=0, k=0, l=0, h2=0, k2=0, l2=0)}"
    assert str(fourc.report) == expected, f"{fourc.report=!r}"

    assert len(fourc.samples) == 1
    assert fourc.sample.name == "cubic"

    fourc.operator.remove_sample("vibranium")
    assert len(fourc.samples) == 1

    fourc.add_sample("vibranium", 2 * pi, digits=3, replace=True)
    assert len(fourc.samples) == 2

    fourc.add_sample("vibranium", 2 * pi, digits=3, replace=True)
    assert len(fourc.samples) == 2
    assert fourc.sample.name == "vibranium"

    fourc.sample = "cubic"
    assert fourc.sample.name == "cubic"

    fourc.sample = "vibranium"
    assert fourc.sample.name == "vibranium"

    assert len(fourc.sample.reflections.order) == 0
    fourc.add_reflection((1, 0, 0), (10, 0, 0, 20), name="r1")
    fourc.add_reflection((0, 1, 0), (10, -90, 0, 20), name="r2")
    assert len(fourc.sample.reflections.order) == 2
    assert fourc.sample.reflections.order == "r1 r2".split()

    fourc.sample.reflections.swap()
    assert fourc.sample.reflections.order == "r2 r1".split()


def test_add_reflections_simple():
    fourc = hklpy2.SimulatedE4CV("", name="fourc")
    fourc.add_reflection((1, 0, 0), (10, 0, 0, 20), name="r1")
    fourc.add_reflection((0, 1, 0), (10, -90, 0, 20), name="r2")
    assert len(fourc.sample.reflections.order) == 2
    assert fourc.sample.reflections.order == "r1 r2".split()

    fourc.sample.reflections.swap()
    assert fourc.sample.reflections.order == "r2 r1".split()
