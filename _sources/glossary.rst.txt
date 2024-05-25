.. include:: /substitutions.txt

.. _glossary:

==========
Glossary
==========

:detector: Measures the intensity of diffracted radiation from the sample.
:diffractometer:
  A *goniometer*.
  The mechanical system of stacked rotation axes used to control a
  sample's crystalline *orientation* and a detector position for
  scientific measurements.

  Generally, there are two stacks, one which controls the *sample* position,
  the other for the *detector* position.

:engine: Some |solver| libraries provide coordinate transformations
  between *reals* and different types of *pseudos*, such as for
  reflectometry or surface scattering.  The |solver| may provide
  an engine for each separate type of transformation (and related
  *pseudos*).

:geometry: The set of *reals* (stacked rotation angles) which
  define a specific *diffractometer*.
  A common distinguishing feature is the number of axes in each stack.
  For example, the :class:`~hklpy2.geom.E4CV` geometry as 3 sample axes
  (``omega``, ``chi``, ``phi``) and 1 detector axis (``tth``).
  In some shorthand reference, this is called "S3D1".

:goniometer: Instrument which allows an object to be rotated to a precise angular position.
:lattice: Lattice parameters of a crystalline *sample*.
:monochromatic: Radiation of a single wavelength.  Or sufficiently narrow
  range, such that it may be characterized by a single floating point value.
:operator: The intermediate software adapter layer between
  :class:`~hklpy2.diffract.DiffractometerBase` (user-facing code) and a
  :class:`~hklpy2.backends.base.SolverBase`.

  Connects a *diffractometer* with  a |solver| library and one of its *geometries*.

:orientation: Positioning of a crystalline sample's atomic planes 
  (identified by a set of *pseudos*) within the laboratory reference
  frame (described by the *reals*).
:pseudo: Reciprocal-space axis, such as :math:`h`, :math:`k`, and :math:`l`.
  The engineering units (rarely examined for crystalline work) are reciprocal
  of the *wavelength* units.
:real: Real-space axis, such as ``omega`` (:math:`\omega`).
  The engineering units are expected to be in **degrees**.
:reflection: User-identified coordinates: (*pseudos*, *reals*, *wavelength*).
  Used to orient a *sample* with a specific *diffractometer* geometry.
:sample: The substance to be explored with the *diffractometer*.
  Has a *lattice* and list of *reflections*.
:solver: Backend |solver| library.  Provides computations to transform
  between *pseudo* and *real* coordinates for a defined
  *diffractometer* *geometry*.
:wavelength: The numerical value of the wavelength of the incident radiation.
  The radiation is expected to be *monochromatic* neutrons or X-rays.
  The engineering units of wavelength must be identical to those of the
  crystalline lattice length parameters: :math:`a`, :math:`b`, & :math:`c`.
