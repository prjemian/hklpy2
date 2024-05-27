.. include:: /substitutions.txt

..  The glossary is formatted as a reST definition list.
    Follow the pattern.

    All glossary entries should be preceded by a
    defining index entry with the same name.

    In a definition, emphasize (wrap with '*') other glossary entries.

.. _glossary:

==========
Glossary
==========

..  index:: !axis, definition; axis

:axis: Either a *pseudo*, *real*, or *extra*.

..  index:: !configuration, definition; configuration

:configuration: Complete description of a *diffractometer's*
  settings.  Includes *solver*, *geometry* (& *engine*, if applicable),
  ordered lists of the *axis* names, dictionaries of *samples*
  (with *lattice* & *reflection(s)*).

..  index:: !detector, definition; detector

:detector: Measures the intensity of diffracted radiation from the sample.

..  index:: !diffractometer, definition; diffractometer

:diffractometer:
  A *goniometer*.
  The mechanical system of stacked rotation axes used to control a
  sample's crystalline *orientation* and a detector position for
  scientific measurements.

  Generally, there are two stacks, one which controls the *sample* position,
  the other for the *detector* position.

..  index:: !engine, definition; engine

:engine: Some |solver| libraries provide coordinate transformations
  between *real* axes and different types of *pseudo* axes,
  such as for reflectometry or surface scattering.  The |solver| may provide
  an engine for each separate type of transformation (and related
  *pseudos*).

..  index:: !extra, definition; extra

:extra: An additional axis used by a |solver| for operation of
  a *diffractometer*.
  For example, when rotating by angle :math:`\psi` around some arbitrary
  diffraction vector, :math:`(h_2,k_2,l_2)`, the extra axes are:
  ``"h2", "k2", "l2", "psi"``.

..  index:: !geometry, definition; geometry

:geometry: The set of *reals* (stacked rotation angles) which
  define a specific *diffractometer*.
  A common distinguishing feature is the number of axes in each stack.
  For example, the :class:`~hklpy2.geom.E4CV` geometry as 3 sample axes
  (``omega``, ``chi``, ``phi``) and 1 detector axis (``tth``).
  In some shorthand reference, this is called "S3D1".

..  index:: !goniometer, definition; goniometer

:goniometer: Instrument which allows an object to be rotated to 
  a precise angular position.

..  index:: !lattice, definition; lattice

:lattice: Lattice parameters of a crystalline *sample*.

..  index:: !monochromatic, definition; monochromatic

:monochromatic: Radiation of a single wavelength.  Or sufficiently narrow
  range, such that it may be characterized by a single floating point value.

..  index:: !operator, definition; operator

:operator: The intermediate software adapter layer between
  :class:`~hklpy2.diffract.DiffractometerBase` (user-facing code) and a
  :class:`~hklpy2.backends.base.SolverBase`.

  Connects a *diffractometer* with  a |solver| library and 
  one of its *geometries*.

..  index:: !orientation, definition; orientation

:orientation: Positioning of a crystalline sample's atomic planes
  (identified by a set of *pseudos*) within the laboratory reference
  frame (described by the *reals*).

..  index:: !pseudo, definition; pseudo

:pseudo: Reciprocal-space axis, such as :math:`h`, :math:`k`, and :math:`l`.
  The engineering units (rarely examined for crystalline work) are reciprocal
  of the *wavelength* units.

..  index:: !real, definition; real

:real: Real-space axis (typically a rotation stage),
  such as ``omega`` (:math:`\omega`).
  The engineering units are expected to be in **degrees**.

..  index:: !reflection, definition; reflection

:reflection: User-identified coordinates: (*pseudos*, *reals*, *wavelength*).
  Used to orient a *sample* with a specific *diffractometer* geometry.

..  index:: !sample, definition; sample

:sample: The named substance to be explored with the *diffractometer*.
  In |hklpy2|, a sample has a *lattice* and list of *reflections*.
  
  The *axes* in a sample's *reflections* are specific to the *diffractometer*
  *geometry*.
  Consequently, the sample is defined for a specific |solver| and
  *geometry*.  The same sample cannot be used for other geometries.

..  index:: !solver, definition; solver

:solver: Backend |solver| library.  Provides computations to transform
  coordinates between *pseudo* and *real* axes for a defined
  *diffractometer* *geometry*.

..  index:: !UB, definition; UB

:UB: Orientation matrix (3 x 3).  

  :math:`U` is the crystal orientation matrix relative to the diffractometer
  
  :math:`B` is the transition matrix of a non-orthonormal
    (the reciprocal of the crystal) in an orthonormal system.

..  index:: !wavelength, definition; wavelength

:wavelength: The numerical value of the wavelength of the incident radiation.
  The radiation is expected to be *monochromatic* neutrons or X-rays.
  The engineering units of wavelength must be identical to those of the
  crystalline lattice length parameters: :math:`a`, :math:`b`, & :math:`c`.
