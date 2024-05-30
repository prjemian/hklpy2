.. include:: /substitutions.txt

.. _api.ops:

==================
Operations
==================

.. index:: !operator

A diffractometer's ``.operator`` provides most of its functionality.
The ``operator`` conducts transactions with the |solver| on behalf of the
diffractometer. These transactions include the ``forward()`` and ``inverse()``
coordinate transformations, at the core of scientific measurements using
a diffractometer.

=============================================   ==============
Python class                                    Purpose
=============================================   ==============
:class:`~hklpy2.diffract.DiffractometerBase`    ophyd `PseudoPositioner <https://blueskyproject.io/ophyd/user/reference/positioners.html#pseudopositioner>`_
:class:`~klpy2.ops.Operations`                  The class for a diffractometer's ``.operator``.
:class:`~hklpy2.backends.base.SolverBase`       Code for diffractometer geometries and capabilities.
=============================================   ==============

In addition to |solver| transactions, the ``.operator`` manages all
details involving the set of samples and their lattices & reflections.

EXAMPLE::

    >>> from hklpy2 import SimulatedE4CV
    >>> e4cv = SimulatedE4CV("", name="e4cv")
    >>> e4cv.operator.sample
    Sample(name='cubic', lattice=Lattice(a=1, b=1, c=1, alpha=90.0, beta=90.0, gamma=90.0))
    >>> e4cv.operator.solver
    HklSolver(name='hkl_soleil', version='v5.0.0.3434', geometry='E4CV', engine='hkl', mode='bissector')
    >>> e4cv.operator.sample.reflections
    {}
    >>> e4cv.add_reflection((1, 0, 0), (10, 0, 0, 20), name="r1")
    Reflection(name='r1', geometry='E4CV', pseudos={'h': 1, 'k': 0, 'l': 0}, reals={'omega': 10, 'chi': 0, 'phi': 0, 'tth': 20}, wavelength=1.0)
    >>> e4cv.add_reflection((0, 1, 0), (10, -90, 0, 20), name="r2")
    Reflection(name='r2', geometry='E4CV', pseudos={'h': 0, 'k': 1, 'l': 0}, reals={'omega': 10, 'chi': -90, 'phi': 0, 'tth': 20}, wavelength=1.0)
    >>> e4cv.operator.sample.reflections
    {'r1': {'name': 'r1', 'geometry': 'E4CV', 'pseudos': {'h': 1, 'k': 0, 'l': 0}, 'reals': {'omega': 10, 'chi': 0, 'phi': 0, 'tth': 20}, 'wavelength': 1.0, 'order': 0}, 'r2': {'name': 'r2', 'geometry': 'E4CV', 'pseudos': {'h': 0, 'k': 1, 'l': 0}, 'reals': {'omega': 10, 'chi': -90, 'phi': 0, 'tth': 20}, 'wavelength': 1.0, 'order': 1}}

..  note:: The :class:`~hklpy2.ops.Operations` class provides
    key diffractometer features as Python properties.  This enables their
    inclusion in the :class:`~hklpy2.diffract.DiffractometerBase` class
    using ophyd `AttributeSignal <https://github.com/bluesky/ophyd/blob/5c03c3fff974dc6390836fc83dae4c247a35e662/ophyd/signal.py#L2192>`_.
    One such example is the |solver| geometry name::

        geometry = Cpt(
            AttributeSignal,
            attr="operator.geometry",
            doc="Name of backend |solver| geometry.",
            write_access=False,
            kind="config",
        )
        """Name of backend |solver| geometry."""

    Using the ``e4cv`` simulator, the property is::

        >>> e4cv.operator.geometry
        'E4CV'

    From the ophyd diffractometer object reports this:

        >>> e4cv.geometry.get()
        'E4CV'


Source Code Documentation
-------------------------

.. automodule:: hklpy2.ops
    :members:
    :private-members:
    :show-inheritance:
    :inherited-members:

