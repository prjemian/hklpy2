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

A *solver* is written as a plugin for |hklpy2| and is connected by an `entry point
<https://setuptools.pypa.io/en/latest/userguide/entry_point.html#entry-points-for-plugins>`_
using the ``"hklpy2.solver"`` group.  Here's an example from |hklpy2|'s
``pyproject.toml`` file for two such Solvers::

    [project.entry-points."hklpy2.solver"]
    no_op = "hklpy2.backends.no_op:NoOpSolver"
    hkl_soleil = "hklpy2.backends.hkl_soleil:HklSolver"

.. _api.backends.set:

How to select a Solver
----------------------

To select a Solver class, call
:func:`~hklpy2.backends.abstract_solver.setSolver`. This example
selects the |libhkl| solver (using its entry point name: ``"hkl_soleil"``)::

    >>> from hklpy2 import setSolver
    >>> Solver = setSolver("hkl_soleil")
    >>> print(f"{Solver=}")
    Solver=<class 'hklpy2.backends.hkl_soleil.HklSolver'>    

To list all available solver classes (by their entry point name), 
call :func:`~hklpy2.backends.abstract_solver.solvers()`.
This example shows the solvers supplied with |hklpy2|::

    >>> from hklpy2 import solvers
    >>> solvers()
    {'hkl_soleil': 'hklpy2.backends.hkl_soleil:HklSolver',
     'no_op': 'hklpy2.backends.no_op:NoOpSolver'}


.. _api.backends.howto:

How to write a new Solver
-------------------------

.. caution:: TODO:: work-in-progress

Solver classes always subclass :class:`~hklpy2.backends.abstract_solver.SolverBase`::

    from hklpy2.backends.SolverBase

    class MySolver(SolverBase):
        ...

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

.. automodule:: hklpy2.backends
    :members:
    :private-members:
    :show-inheritance:
    :inherited-members:

.. automodule:: hklpy2.backends.abstract_solver
    :members:
    :private-members:
    :show-inheritance:
    :inherited-members:

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
