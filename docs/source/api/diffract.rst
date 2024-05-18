.. include:: /substitutions.txt

.. _api.diffract:

==================
Diffractometer
==================

:concept: User builds a subclass of :class:`~hklpy2.diffract.Diffractometer()`,
  adding a variety of positioners as ophyd Components.  In an instance of that
  subclass, user selects a backend |solver| and defines which Components are to
  be used as pseudos, reals, and extras.  The backend implements ``forward()`` and
  ``inverse()`` and all related support, for only the pseudos, reals, and extras
  that are identified.

.. note:: Define a ``@needs_solver`` decorator to test these needs.

.. grid:: 2

    .. grid-item-card:: :material-outlined:`check_box;3em` A |solver| is not needed to:

      - define a diffractometer subclass
      - define a sample
      - define a lattice
      - review available solvers
      - review saved orientation details

    .. grid-item-card:: :material-outlined:`rule;3em` A |solver| is needed to:

      - list available geometries
      - list a geometry's required pseudos, reals, extras, modes
      - define a reflection
      - compute a :math:`UB` matrix
      - ``forward()`` and ``inverse()``
      - refine lattice parameters
      - determine the diffractometer ``.position``
      - save or restore orientation details

Source Code Documentation
-------------------------

.. automodule:: hklpy2.diffract
    :members:
    :private-members:
    :show-inheritance:
    :inherited-members:

