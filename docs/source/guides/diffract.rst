.. _diffract_axes:

=========================
Diffractometer Axis Names
=========================

In |hklpy2|, the names of diffractometer axes (pseudos and reals) are
not required to match any particular |solver| library.  Users are free
to use any names allowed by ophyd.

User-defined axis names
-----------------------

Let's see examples of diffractometers built with user-defined names.

* :ref:`diffract_axes.diffractometer-factory` with automatic mapping
* :ref:`diffract_axes.direct-assign` with directed mapping

.. _diffract_axes.diffractometer-factory:

Diffractometer Creator
+++++++++++++++++++++++++++++++

The :func:`~hklpy2.geom.creator()` creates a diffractometer object using the
supplied `reals={}` to define their names.  These are mapped to the names used
by the |solver|.  Let's show this cross-reference map with just a few commands::

    >>> import hklpy2

    >>> twoc = hklpy2.creator(
        name="twoc",
        geometry="TH TTH Q",
        solver="th_tth",
        reals={"sample": None, "detector": None},
    )

    >>> twoc.core.axes_xref
    {'q': 'q', 'sample': 'th', 'detector': 'tth'}

    >>> twoc.wh()
    q=0
    wavelength=1.0
    sample=0, detector=0

.. _diffract_axes.custom-assign:

Custom Diffractometer class
+++++++++++++++++++++++++++++++++++++

.. TODO #51

Construct a 2-circle diffractometer, one axis for the sample and one axis for
the detector.

In addition to defining the diffractometer axes, we name the |solver| to use
with our diffractometer. The ``th_tth`` |solver| has a
:class:`~hklpy2.backends.th_tth_q.ThTthSolver` with a ``"TH TTH Q"`` geometry
that fits our design. We set that up in the ``__init__()`` method of our new
class:

.. code-block:: Python
    :linenos:

    import hklpy2
    from ophyd import Component, PseudoSingle, SoftPositioner

    class S1D1(hklpy2.DiffractometerBase):

        q = Component(PseudoSingle, "", kind=H_OR_N)

        sample = Component(SoftPositioner, init_pos=0)
        detector = Component(SoftPositioner, init_pos=0)

        _real = ["sample", "detector"]  # Maps 'sample' to 'th', 'detector' to 'tth'

        def __init__(self, *args, **kwargs):
            super().__init__(
                *args,
                solver="th_tth",                # solver name
                geometry="TH TTH Q",            # solver geometry
                **kwargs,
            )

Create a Python object that uses this class:

.. code-block:: Python

    twoc = S1D1(name="twoc")

.. tip:: Use the :func:`hklpy2.geom.creator()` instead:

    .. code-block:: Python

        twoc = hklpy2.creator(
            name="twoc",
            geometry="TH TTH Q",
            solver="th_tth",
            reals=dict(sample=None, detector=None)
        )

Show the mapping between user-defined axes and axis names used by the |solver|::

    >>> print(twoc.core.axes_xref)
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

.. code-block:: Python
    :linenos:

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

        _pseudo = ["q"]  # TODO: #51
        _real = ["theta", "ttheta"]

        def __init__(self, *args, **kwargs):
            super().__init__(
              *args,
              solver="th_tth",
              geometry="TH TTH Q",
              **kwargs
              )

Create the diffractometer:

.. code-block:: Python

    twoc = MyTwoC(name="twoc")

What are the axes names used by this diffractometer?

.. code-block:: Python

    >>> twoc.pseudo_axis_names
    ['another', 'q']
    >>> twoc.real_axis_names
    ['horizontal', 'theta', 'ttheta', 'vertical']

Show the ``twoc`` diffractometer's |solver|:

.. code-block:: Python

    >>> twoc.core.solver
    ThTthSolver(name='th_tth', version='0.0.14', geometry='TH TTH Q')

What are the axes expected by this |solver|?

.. code-block:: Python

    >>> twoc.core.solver.pseudo_axis_names
    ['q']
    >>> twoc.core.solver.real_axis_names
    ['th', 'tth']
    >>> twoc.core.solver.extra_axis_names
    []

Show the cross-reference mapping from diffractometer
to |solver| axis names (as defined in our MyTwoC class above):

.. code-block:: Python

    >>> twoc.core.axes_xref
    {'q': 'q', 'theta': 'th', 'ttheta': 'tth'}
