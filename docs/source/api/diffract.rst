.. include:: /substitutions.txt

.. _api.diffract:

==================
Diffractometer
==================

.. caution:: work-in-progress

.. index:: !design; diffractometer

:concept: User builds a subclass of
  :class:`~hklpy2.diffract.DiffractometerBase()`, adding a variety of
  positioners as ophyd Components.  In an instance of that subclass, user
  sets :attr:`~hklpy2.diffract.DiffractometerBase.backend_solver` by calling
  :func:`~hklpy2.operations.misc.solver_factory`.  In this call, the user specifies the solver,
  the geometry, and defines which Components (of the diffractometer) are to be used as
  pseudos, reals, and extras.  The backend implements
  :meth:`~hklpy2.backends.base.SolverBase.forward`,
  :meth:`~hklpy2.backends.base.SolverBase.inverse`, and all related support, for
  only the pseudos, reals, and extras that are identified.

.. grid:: 2

    .. grid-item-card:: :material-outlined:`check_box;3em` A |solver| is not needed to:

      - define subclass of :class:`~hklpy2.diffract.DiffractometerBase()` and create instance
      - create instance of :class:`~hklpy2.operations.sample.Sample()`
      - create instance of :class:`~hklpy2.operations.lattice.Lattice()`
      - create instance of :class:`~hklpy2.wavelength_support.WavelengthBase()` subclass
      - create instance of :class:`~hklpy2.backends.base.SolverBase()` subclass
      - set :attr:`~hklpy2.wavelength_support.WavelengthBase.wavelength`
      - list *available* solvers: (:func:`~hklpy2.operations.misc.solvers`)
      - review saved orientation details

    .. grid-item-card:: :material-outlined:`rule;3em` A |solver| is needed to:

      - list available |solver| :attr:`~hklpy2.backends.base.SolverBase.geometries`
      - list a |solver| geometry's required
        :attr:`~hklpy2.backends.base.SolverBase.pseudo_axis_names`,
        :attr:`~hklpy2.backends.base.SolverBase.real_axis_names`,
        :attr:`~hklpy2.backends.base.SolverBase.extra_axis_names`,
        :attr:`~hklpy2.backends.base.SolverBase.modes`
      - create instance of :class:`~hklpy2.operations.reflection.Reflection()`
      - define or compute a :math:`UB` matrix
        (:meth:`~hklpy2.backends.base.SolverBase.calculateOrientation`)
      - :meth:`~hklpy2.backends.base.SolverBase.forward`
        and :meth:`~hklpy2.backends.base.SolverBase.inverse`
      - determine the diffractometer :attr:`~hklpy2.diffract.DiffractometerBase.position`
      - save or restore orientation details
      - refine lattice parameters

The :class:`~hklpy2.diffract.DiffractometerBase()` class should
be a thin interface. Most real diffractometer capability should be
provided in the :class:`~hklpy2.ops.Operations()` class (or one of
its attributes, such as :attr:`~hklpy2.ops.Operations.solver`
and :attr:`~hklpy2.ops.Operations.sample`)

.. rubric:: Operations-related methods and properties
.. autosummary::

    ~hklpy2.diffract.DiffractometerBase.add_sample (method)
    ~hklpy2.ops.Operations.set_solver (method)
    ~hklpy2.diffract.DiffractometerBase.auto_assign_axes (method)

.. rubric:: Sample-related methods and properties
.. autosummary::

    ~hklpy2.diffract.DiffractometerBase.add_sample (method)
    ~hklpy2.diffract.DiffractometerBase.sample (property)
    ~hklpy2.diffract.DiffractometerBase.samples (property)

.. rubric:: Solver-related methods and properties
.. autosummary::

    ~hklpy2.diffract.DiffractometerBase.geometry (ophyd Signal)
    ~hklpy2.ops.Operations.set_solver (method)
    ~hklpy2.diffract.DiffractometerBase.solver (property)
    ~hklpy2.diffract.DiffractometerBase.solver_name (ophyd Signal)

Source Code Documentation
-------------------------

.. automodule:: hklpy2.diffract
    :members:
    :private-members:
    :show-inheritance:

Inherited members, from ``ophyd.PseudoPositioner``
+++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. so many inherited members, list separately

.. automodule:: hklpy2.diffract
    :inherited-members:
    :no-index:

