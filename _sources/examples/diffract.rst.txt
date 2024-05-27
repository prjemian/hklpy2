.. include:: /substitutions.txt

.. _diffract_axes:

=========================
Diffractometer Axis Names
=========================

In |hklpy2|, the names of diffractometer axes (pseudos and reals) are
not required to match any particular |solver| library.  Users are free
to use any names allowed by ophyd.

User-defined axis names
--------------------------------

Let's a few examples of diffractometers built with user-defined names.

* :ref:`diffract_axes.prebuilt-auto-assign` with automatic mapping
* :ref:`diffract_axes.custom-auto-assign` with automatic mapping
* :ref:`diffract_axes.direct-assign` where direct the mapping

.. seealso:: :ref:`diffract_axes.auto-assign`

.. _diffract_axes.prebuilt-auto-assign:

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

.. _diffract_axes.custom-auto-assign:

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

.. _diffract_axes.direct-assign:

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
.. _diffract_axes.auto-assign:

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
