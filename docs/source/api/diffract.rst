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

Regarding user-defined axis names, the
:class:`~hklpy2.diffract.DiffractometerBase` subclass is defined
with the user names.  Consider this example for a two-circle
class (with some extra axes).
The ``"TH TTH Q"`` |solver| geometry expects ``q`` as
the only pseudo axis and ``th`` and ``tth`` as the two real axes
(no extra axes).

::

    from ophyd import Component, PseudoSingle, SoftPositioner
    import hklpy2

    class MyTwoC(hklpy2.DiffractometerBase):

        # sorted alphabetically for this example
        another = Component(PseudoSingle)
        horizontal = Component(SoftPositioner, init_pos=0)
        q = Component(PseudoSingle)
        theta = Component(SoftPositioner, init_pos=0)
        ttheta = Component(SoftPositioner, init_pos=0)
        vertical = Component(SoftPositioner, init_pos=0)

        def __init__(self, *args, **kwargs):
            super().__init__(
              *args,
              solver="th_tth",
              geometry="TH TTH Q",
              pseudos=["q"],
              reals=["theta", "ttheta"],
              **kwargs
              )

Create the diffractometer::

    twoc = MyTwoC("", name="twoc")

What are the axes names used by this diffractometer?::

    >>> twoc.pseudo_axis_names
    ['another', 'q']
    >>> twoc.real_axis_names
    ['horizontal', 'theta', 'ttheta', 'vertical']

Show the ``twoc`` diffractometer's |solver|::

    >>> twoc.operator.solver
    ThTthSolver(name='th_tth', version='0.0.14', geometry='TH TTH Q')

What are the axes expected by this |solver|?::

    >>> twoc.operator.solver.pseudo_axis_names
    ['q']
    >>> twoc.operator.solver.real_axis_names
    ['th', 'tth']
    >>> twoc.operator.solver.extra_axis_names
    []

Show the cross-reference mapping from diffractometer
to |solver| axis names (as defined in our MyTwoC class above)::

    >>> twoc.operator.axes_xref
    {'q': 'q', 'theta': 'th', 'ttheta': 'tth'}

Auto-assignment assigns the first pseudo(s), real(s), and extra(s)
defined by the diffractometer as needed by the |solver|.
In our diffractometer class (MyTwoC), the axes are sorted alphabetically.
Auto-assignment of axes would not have been correct, because we did not
define the ``q`` axis Component as the first pseudo and ``theta`` & ``ttheta``
as the first real axis Components.  Let's show what auto-assignment
chooses in this case::

    >>> twoc.auto_assign_axes()
    >>> twoc.operator.axes_xref
    {'another': 'q', 'horizontal': 'th', 'theta': 'tth'}

.. rubric:: Operations-related methods and properties
.. autosummary::

    ~hklpy2.diffract.DiffractometerBase.add_sample
    ~hklpy2.diffract.DiffractometerBase.set_solver
    ~hklpy2.diffract.DiffractometerBase.auto_assign_axes

.. rubric:: Sample-related methods and properties
.. autosummary::

    ~hklpy2.diffract.DiffractometerBase.add_sample
    ~hklpy2.diffract.DiffractometerBase.sample
    ~hklpy2.diffract.DiffractometerBase.samples

.. rubric:: Solver-related methods and properties
.. autosummary::

    ~hklpy2.diffract.DiffractometerBase.geometry
    ~hklpy2.diffract.DiffractometerBase.set_solver
    ~hklpy2.diffract.DiffractometerBase.solver
    ~hklpy2.diffract.DiffractometerBase.solver_name

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

