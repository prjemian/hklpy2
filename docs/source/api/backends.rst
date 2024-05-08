.. include:: /substitutions.txt

.. index::!Solver class

.. _api.backends:

==================
Backend Solvers
==================

A |solver| is a Python class that connects |hklpy2| with a (backend) library
that provides diffractometer capabilities, including:

* definition(s) of physical diffractometer **geometries**

  * axes (angles and reciprocal space)
  * operating **modes** for the axes (angles and reciprocal space)

* calculations that convert:

  * **forward**: reciprocal space coordinates into diffractometer angles
  * **inverse**: diffractometer angles into reciprocal space coordinates

* support operations include:

  * calculate the UB matrix
  * refine the crystal lattice
  * sample definition

    * name
    * crystal lattice parameters: :math:`a, b, c, \alpha, \beta, \gamma`
    * list of orientation reflections

A |solver| class is written as a plugin for |hklpy2| and is connected by an `entry point
<https://setuptools.pypa.io/en/latest/userguide/entry_point.html#entry-points-for-plugins>`_
using the ``"hklpy2.solver"`` group.  Here's an example from |hklpy2|'s
``pyproject.toml`` file for two such |solver| classes::

    [project.entry-points."hklpy2.solver"]
    no_op = "hklpy2.backends.no_op:NoOpSolver"
    hkl_soleil = "hklpy2.backends.hkl_soleil:HklSolver"

.. _api.backends.set:

How to select a Solver
----------------------

To select a |solver| class, call
:func:`~hklpy2.backends.base.get_solver`. This example
selects the |libhkl| |solver| (using its entry point name: ``"hkl_soleil"``)::

    >>> from hklpy2 import get_solver
    >>> Solver = get_solver("hkl_soleil")
    >>> print(f"{Solver=}")
    Solver=<class 'hklpy2.backends.hkl_soleil.HklSolver'>    

To list all available |solver| classes (by their entry point name), 
call :func:`~hklpy2.backends.base.solvers()`.
This example shows the |solver| classes supplied with |hklpy2|::

    >>> from hklpy2 import solvers
    >>> solvers()
    {'hkl_soleil': 'hklpy2.backends.hkl_soleil:HklSolver',
     'no_op': 'hklpy2.backends.no_op:NoOpSolver'}

.. _api.backends.howto:

How to write a new Solver
-------------------------

.. caution:: TODO:: work-in-progress

|solver| classes always subclass :class:`~hklpy2.backends.base.SolverBase`::

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


.. toctree::
   :glob:
   :hidden:

   backends/*

Source Code Documentation
-------------------------

.. automodule:: hklpy2.backends
    :members:
    :private-members:
    :show-inheritance:
    :inherited-members:

