.. include:: /substitutions.txt

.. _api.diffract:

==================
Diffractometer
==================

.. caution:: work-in-progress

:concept: User builds a subclass of
  :class:`~hklpy2.diffract.DiffractometerBase()`, adding a variety of
  positioners as ophyd Components.  In an instance of that subclass, user
  sets :attr:`~hklpy2.diffract.DiffractometerBase.backend_solver` by calling
  :func:`~hklpy2.misc.solver_factory`.  In this call, the user specifies the solver,
  the geometry, and defines which Components (of the diffractometer) are to be used as
  pseudos, reals, and extras.  The backend implements
  :meth:`~hklpy2.backends.base.SolverBase.forward`,
  :meth:`~hklpy2.backends.base.SolverBase.inverse`, and all related support, for
  only the pseudos, reals, and extras that are identified.

.. grid:: 2

    .. grid-item-card:: :material-outlined:`check_box;3em` A |solver| is not needed to:

      - define subclass of :class:`~hklpy2.diffract.DiffractometerBase()` and create instance
      - create instance of :class:`~hklpy2.sample.Sample()`
      - create instance of :class:`~hklpy2.lattice.Lattice()`
      - create instance of :class:`~hklpy2.wavelength_support.WavelengthBase()` subclass
      - create instance of :class:`~hklpy2.backends.base.SolverBase()` subclass
      - set :attr:`~hklpy2.wavelength_support.WavelengthBase.wavelength`
      - list *available* solvers: (:func:`~hklpy2.misc.solvers`)
      - review saved orientation details

    .. grid-item-card:: :material-outlined:`rule;3em` A |solver| is needed to:

      - list available |solver| :attr:`~hklpy2.backends.base.SolverBase.geometries`
      - list a |solver| geometry's required 
        :attr:`~hklpy2.backends.base.SolverBase.pseudo_axis_names`,
        :attr:`~hklpy2.backends.base.SolverBase.real_axis_names`,
        :attr:`~hklpy2.backends.base.SolverBase.extra_axis_names`,
        :attr:`~hklpy2.backends.base.SolverBase.modes`
      - create instance of :class:`~hklpy2.reflection.Reflection()`
      - define or compute a :math:`UB` matrix
        (:meth:`~hklpy2.backends.base.SolverBase.calculateOrientation`)
      - :meth:`~hklpy2.backends.base.SolverBase.forward`
        and :meth:`~hklpy2.backends.base.SolverBase.inverse`
      - determine the diffractometer :attr:`~hklpy2.diffract.DiffractometerBase.position`
      - save or restore orientation details
      - refine lattice parameters

      .. note:: Add ``@needs_solver`` decorator for these actions.

Regarding user-defined axis names, the 
:class:`~hklpy2.diffract.DiffractometerBase`` subclass is defined
with the user names.  Consider this example for a two-circle
class (with some extra axes)::

    class MyTwoC(DiffractometerBase):
        """Test case."""

        d_spacing = Component(PseudoSingle)
        q = Component(PseudoSingle, "")
        theta = Component(SoftPositioner)
        ttheta = Component(SoftPositioner)
        x = Component(SoftPositioner, "")

    twoc = MyTwoC("", name="twoc")

When creating the |solver| instance, the caller specifies the required axes in
the order expected by the |solver|. The ``"TH TTH Q"`` geometry expects ``q`` as
the only pseudo axis and ``th`` and ``tth`` as the two real axes (no extra axes).
Connect the user-defined axes of the diffractometer with the axes in the order
expected by the solver like this::

    from hklpy2 import solver_factory
    twoc.backend_solver = solver_factory(
        "th_tth",
        "TH TTH Q",
        pseudos=[twoc.q],
        reals=[twoc.theta, twoc.ttheta],
        extras=[],
    )

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

