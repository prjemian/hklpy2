.. _concepts:

==========
Concepts
==========

.. toctree::
   :glob:
   :hidden:

   concepts/*

.. figure:: _static/hklpy2-block-diagram.png
   :alt: hklpy2 block diagram

   Functional blocks in  |hklpy2|.

Overview
========

The |hklpy2| *diffractometer* [#]_ is an ophyd *PseudoPositioner*, [#]_
providing both *pseudo* coordinates and *real* coordinates.  Movement in one
coordinate space updates the coordinates of the other space.  For
diffractometers, the orientation matrix ($UB$) enables transformation between the
two spaces.

.. note:: A monochromatic [#]_ radiation source is expected.

.. rubric:: Coordinates

:pseudos:
   Virtual coordinates (crystallographic `h`, `k`, `l`), computed from *reals*.
:reals:
   Positioners (rotation motors) in physical coordinates.

An ophyd *PseudoPositioner* transforms between *pseudos* and *reals*
with the :meth:`~hklpy2.diffract.DiffractometerBase.forward()` and
:meth:`~hklpy2.diffract.DiffractometerBase.inverse()` methods.

.. rubric:: Transformations

==========  =========   ============== ======== ================
from        to          transformation solution implementation
==========  =========   ============== ======== ================
*reals*     *pseudos*   transformation unique   :meth:`~hklpy2.diffract.DiffractometerBase.inverse()`
*pseudos*   *reals*     transformation many     :meth:`~hklpy2.diffract.DiffractometerBase.forward()`
==========  =========   ============== ======== ================

.. seealso:: :ref:`glossary`

.. [#] https://en.wikipedia.org/wiki/Diffractometer
.. [#] https://blueskyproject.io/ophyd/user/how-to/pseudopositioner.html
.. [#] *monochromatic*: The range of wavelengths in the source is negligible
   for scientific interpretation.
