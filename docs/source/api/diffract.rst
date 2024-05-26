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

.. Looks more like a howto than API docs

User-defined axis names
--------------------------------

In |hklpy2|, the names of diffractometer axes are not required to match
any particular |solver| library.  Let's show that with a few examples.

* :ref:`diffract.prebuilt-auto-assign` with automatic mapping
* :ref:`diffract.custom-auto-assign` with automatic mapping
* :ref:`diffract.direct-assign` where direct the mapping

.. seealso:: :ref:`diffract.auto-assign`

.. _diffract.prebuilt-auto-assign:

Pre-built Diffractometer class
+++++++++++++++++++++++++++++++++++++

The pre-built diffractometer simulators automatically 
map axis names from diffractometer to |solver|.  Let's show this
cross-reference map in an IPython console with just a few commands
(using :class:`~hklpy2.geom.SimulatedTheta2Theta`)::

    In [6]: from hklpy2 import SimulatedTheta2Theta

    In [7]: twoc = SimulatedTheta2Theta("", name="twoc")

    In [8]: twoc.operator.axes_xref
    Out[8]: {'q': 'q', 'theta': 'th', 'ttheta': 'tth'}

.. _diffract.custom-auto-assign:

Custom Diffractometer class
+++++++++++++++++++++++++++++++++++++

Construct a 2-circle diffractometer, one axis for the sample
and one axis for the detector.  We can use the 
:class:`~hklpy2.geom.MixinQ` class to define a ``q`` pseudo-axis.

In addition to defining the diffractometer axes, we can choose the
|solver| to use with our diffractometer.
The ``th_tth`` |solver| has a :class:`~hklpy2.backends.th_tth_q.ThTthSolver` 
with a ``"TH TTH Q"`` geometry that fits our design.
We set that up in the ``__init__()`` method of our new class::

    import hklpy2
    from ophyd import Component
    from ophyd import SoftPositioner

    class S1D1(hklpy2.DiffractometerBase, hklpy2.MixinQ):

        sample = Component(SoftPositioner, init_pos=0)
        detector = Component(SoftPositioner, init_pos=0)

        def __init__(self, *args, **kwargs):
            super().__init__(
                *args,
                solver="th_tth",                #  solver name
                geometry="TH TTH Q",            # solver geometry
                **kwargs,
            )
            self.operator.auto_assign_axes()    # assign axes

Create a Python object that uses this class::

    twoc = S1D1("", name="twoc")

Show the mapping between user-defined axes and axis names used by the |solver|::

    >>> print(twoc.operator.axes_xref)
    {'q': 'q', 'sample': 'th', 'detector': 'tth'}

.. _diffract.direct-assign:

Custom Diffractometer with additional axes
++++++++++++++++++++++++++++++++++++++++++++++++

Consider this example for a two-circle class (with additional axes).
The ``"TH TTH Q"`` |solver| geometry expects ``q`` as
the only pseudo axis and ``th`` and ``tth`` as the two real axes
(no extra axes).

We construct this example so that we'll need to override the
automatic assignment of axes. Look for the ``pseudos=["q"]``
and ``reals=["theta", "ttheta"]`` parts where we define the mapping.

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

..  index:: 
    !auto-assign axes
    !axis names
.. _diffract.auto-assign:

Auto-assignment
++++++++++++++++++

In |hklpy2|, the names of diffractometer axes are not required to match
any particular |solver| library.

Auto-assignment assigns the first pseudo(s), real(s), and extra(s)
defined by the diffractometer as needed by the |solver|.

.. seealso:: :meth:`~hklpy2.diffract.DiffractometerBase.auto_assign_axes`

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

