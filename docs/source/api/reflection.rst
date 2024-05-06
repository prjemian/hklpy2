.. _api.reflection:

==================
Reflection
==================

A reflection is a peak intensity (typically an observation) due to diffraction
from a specific orientation of a crystalline sample with respect to the incident
radiation. The reflection occurs for a precise alignment of crystalline planes
and diffractometer axes with the incoming beam. The coordinates of two or more
reflections in both real and reciprocal space are used to determine the
:math:`UB` orientation matrix.

Each reflection is defined by:

* full set of diffractometer angles - *real axes*
* reciprocal-space coordinates - *pseudo axes*
* wavelength of the incident radiation

Note that the engineering units for the pseudo axes are the reciprocal of the
units of the wavelength (where *angstroms* is typical).  The angles are reported
in *degrees*.

Source Code Documentation
-------------------------

.. automodule:: hklpy2.reflection
    :members:
    :private-members:
    :show-inheritance:
    :inherited-members:

