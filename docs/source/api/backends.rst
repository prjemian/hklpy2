.. include:: /substitutions.txt

.. _api.backends:

==================
Backend Solvers
==================

A backend (or solver) is a Python class that connects |hklpy2| with a library
backend that provides diffractometer capabilities:

* definition(s) of physical diffractometer **geometries**
* calculation *engines* that convert:

  * **forward**: reciprocal space coordinates into diffractometer angles
  * **inverse**: diffractometer angles into reciprocal space coordinates

* engine-based operating **modes** for the axes (angles and reciprocal space)
* support functions include:

  * calculate the UB matrix
  * refine the crystal lattice

A solver is written as a plugin for |hklpy2| and is connected by an `entry point
<https://setuptools.pypa.io/en/latest/userguide/entry_point.html#entry-points-for-plugins>`_
using the ``"hklpy2.solver"`` group.  Here's an example from the |hklpy2|'s
``pyproject.toml`` file for two such Solvers::

    [project.entry-points."hklpy2.solver"]
    no_op = "hklpy2.backends.no_op:NoOpSolver"
    hkl_soleil = "hklpy2.backends.hkl_soleil:HklSolver"

.. TODO: How to write a new Solver

.. TODO: Collected considerations for Solvers
    - https://github.com/bluesky/hklpy/issues/14
    - https://github.com/bluesky/hklpy/issues/161
    - https://github.com/bluesky/hklpy/issues/162
    - https://github.com/bluesky/hklpy/issues/163
    - https://github.com/bluesky/hklpy/issues/165
    - https://github.com/bluesky/hklpy/issues/244
    - https://xrayutilities.sourceforge.io/
    - https://cohere.readthedocs.io
    - https://github.com/AdvancedPhotonSource/cohere-scripts/tree/main/scripts/beamlines/aps_34idc
    - https://xrayutilities.sourceforge.io/_modules/xrayutilities/experiment.html#QConversion
    - https://github.com/DiamondLightSource/diffcalc
    - SPEC server mode
    - https://github.com/prjemian/pyub

Source Code Documentation
-------------------------

.. automodule:: hklpy2.backends.hkl_soleil
    :members:
    :private-members:
    :show-inheritance:
    :inherited-members:

.. automodule:: hklpy2.backends.no_op
    :members:
    :private-members:
    :show-inheritance:
    :inherited-members:
