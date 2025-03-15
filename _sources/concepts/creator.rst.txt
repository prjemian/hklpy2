.. _concepts.creator:

======================
Diffractometer creator
======================

The :func:`~hklpy2.diffract.creator()`, a `factory function
<https://en.wikipedia.org/wiki/Factory_(object-oriented_programming)>`_, reduces
the effort to create all but the most complex diffractometer objects. It uses
the :func:`~hklpy2.diffract.diffractometer_class_factory()` to build the Python
class for those chosen |solver| and geometry.

.. rubric:: Examples

See :ref:`examples` for many documents which use the
:func:`~hklpy2.diffract.creator()` factory function.
Here's a sampler:

=============================== ====================
diffractometer description      example
=============================== ====================
simple                          :doc:`/examples/hkl_soleil-e4cv`
geometry                        :doc:`/examples/hkl_soleil-k4cv`
solver                          :doc:`/examples/_api_demo`
engine (via ``solver_kwargs``)  :doc:`/examples/hkl_soleil-e6c-psi`
EPICS PVs                       tbd
renamed axes                    :doc:`/examples/nslsii-tardis`
additional reals                :doc:`/examples/hkl_soleil-e6c-psi`
auto assign                     tbd
reals out of order              tbd
extras                          :doc:`/examples/hkl_soleil-e6c-psi`
=============================== ====================
