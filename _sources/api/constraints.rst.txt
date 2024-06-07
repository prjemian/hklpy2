.. include:: /substitutions.txt

.. index::
    !constraint
    mode

.. _api.Constraints:

==================
Constraints
==================

.. note:: This module is not available yet.

Computation of the real-space axis positions given a set of
reciprocal-space coordinates can have many solutions. One or more
constraints (Constraint) (a.k.a, cut points), together with a choice of
operating *mode*, can be applied to:

* limit the range of ``forward()`` solutions accepted for that positioner
* declare the value to use when the positioner should be kept constant

..
    Source Code Documentation
    -------------------------

    .. automodule :: hklpy2.operations.constraints
        :members:
        :private-members:
        :show-inheritance:
        :inherited-members:

