.. include:: /substitutions.txt

.. _api.diffract:

==================
Diffractometer
==================

:concept: User builds a subclass of :class:`~hklpy2.diffract.Diffractometer()`,
adding a variety of positioners as ophyd Components.  In an instance of that subclass,
user selects a backend |solver| and defines which Components are to be used as pseudos, reals,
and extras.  The backend implements `forward()` and `inverse()` and all related support.

.. grid:: 2

    .. grid-item-card:: :material-outlined:`check_box;3em` A |solver| is **not** needed to:

      - define a diffractometer subclass
      - define a sample
      - define a lattice
      - learn what solvers are available

    .. grid-item-card:: :material-outlined:`rule;3em` A |solver| is needed to:

      - list required geometries, pseudos, reals, extras, modes
      - define a reflection
      - compute a :math:`UB` matrix
      - refine lattice parameters
      - determine the diffractometer `.position`

Source Code Documentation
-------------------------

.. automodule:: hklpy2.diffract
    :members:
    :private-members:
    :show-inheritance:
    :inherited-members:

