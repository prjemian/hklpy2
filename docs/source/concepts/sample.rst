.. _concepts.sample:

======
Sample
======

A sample has a name, lattice, reflections, and orientation.

TODO: Describe the concepts

.. _sample.examples:

Examples
++++++++

TODO: Duplicate of E4CV example?

We limit our examples here to just a few brief examples will show how to
define a sample, its crystal lattice, and orient the crystal to position
it using reciprocal space coordinates.  We'll leave it to others (for
now) to show more comprehensive examples that show additional
capabilities, such as limiting the ranges of the motors for acceptable
solutions of the *forward* calculation from $hkl$ to motor positions.

These examples use a diffractometer object called ``fourc`` which we'll take to
be an instance of a 4-circle diffractometer in vertical scattering geometry
(:ref:`E4CV <geometries-hkl_soleil-e4cv>`) with simulated motors.  (This is
similar to the 6-circle example
:doc:`/examples/hkl_soleil-e6c-test_calculations`.)

.. code-block:: python
    :linenos:

    import hklpy2

    fourc = hklpy2.creator(name='fourc')

define a sample with a lattice
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Define a sample with the name *EuPtIn4_eh1_ver* and define its
crystal lattice.  Use angstroms as units for the unit cell edges
and degrees for the angles.

.. code-block:: python
    :linenos:

    from hkl import Lattice
    fourc.add_sample('EuPtIn4_eh1_ver', a=4.542, b=16.955, c=7.389)

The :class:`hklpy2.blocks.lattice.Lattice()` class has defaults for the lattice
parameters.  We only need to provided the parts that are different.  The code
will identify the crystal system.  Inconsistent lattice parameters will raise an
exception.

define an orientation matrix
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is a brief example to define two reflections and then
apply the method of Busing & Levy [#]_ to calculate
an orientation matrix.

For this example, the reflection positions were found
at a wavelength of 1.62751693358 angstroms.

.. code-block:: python
    :linenos:

    fourc.wavelength.put(1.62751693358)

We found the (*080*) reflection at these motor positions:

.. code-block:: python
    :linenos:

    p = dict(omega=22.31594, chi=89.1377, phi=0, tth=45.15857)

Associate `p` (the motor positions) with the (*080*) reflection::

    r1 = fourc.add_reflection((0, 8, 0), p, name="r080")

Do the same for the (*0 12 1*) reflection::

    p = dict(omega=34.96232, chi=78.3139, phi=0, tth=71.8007)
    r2 = fourc.add_reflection((0, 12, 1), p, name="r_0_12_1")

Compute the **UB** matrix::

    fourc.core.calc_UB(r1, r2)

See the **hkl_soleil** documentation [#]_ for more details.

.. [#] Acta Cryst 22 (1967) 457-464
.. [#] **hkl_soleil** documentation:
    https://people.debian.org/~picca/hkl/hkl.html

compute the motor positions for a reflection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Compute the motor positions for the (*100*) reflection::

    fourc.forward(1,0,0)

This can be assigned to a python object::

    p = fourc.forward(0,1,1)

Then, the motor positions can be accessed: ``p.omega``, ``p.chi``,
``p.phi``, ``p.tth``.

These are the motor angles computed as the first solution:

========= ======== ======== ========= ========
(hkl)     omega    chi      phi       tth
========= ======== ======== ========= ========
(1, 0, 0) 10.32101 0.20845  86.38310  20.64202
========= ======== ======== ========= ========
