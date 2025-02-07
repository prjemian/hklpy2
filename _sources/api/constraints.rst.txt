.. include:: /substitutions.txt

.. index::
    !constraint
    mode

.. _api.Constraints:

===========
Constraints
===========

Computation of the real-space axis positions given a set of reciprocal-space
coordinates can have many solutions. One or more constraints (Constraint)
(a.k.a, cut points), together with a choice of operating *mode*, can:

* Limit the range of ``forward()`` solutions accepted for that positioner.
* Declare the value to use when the positioner should be kept constant. (not implemented yet)

Source Code Documentation
-------------------------

.. automodule :: hklpy2.operations.constraints
    :members:
    :private-members:
    :show-inheritance:
    :inherited-members:
