.. include:: /substitutions.txt

.. _api.User:

==================
User Friendliness
==================

Make it easier for users (especially SPEC users) to learn and remember
the tools in Bluesky's |hklpy2| package.

Quickstart
----------

Make a diffractometer (simulator) and show its initial setting.

.. code-block:: python
    :linenos:

    >>> import hklpy2
    >>> sixc = hklpy2.creator(name="sixc", geometry="E6C")

Add the user interface support:

.. code-block:: python

    >>> from hklpy2.user import *

Set the ``sixc`` as the diffractometer:

.. code-block:: python

    >>> set_diffractometer(sixc)

Report all (current) settings of ``sixc``:

.. code-block:: python
    :linenos:

    >>> pa()
    diffractometer='sixc'
    HklSolver(name='hkl_soleil', version='5.1.2', geometry='E6C', engine_name='hkl', mode='bissector_vertical')
    Sample(name='sample', lattice=Lattice(a=1, system='cubic'))
    U=[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    UB=[[6.28318530718, -0.0, -0.0], [0.0, 6.28318530718, -0.0], [0.0, 0.0, 6.28318530718]]
    constraint: -180.0 <= mu <= 180.0
    constraint: -180.0 <= omega <= 180.0
    constraint: -180.0 <= chi <= 180.0
    constraint: -180.0 <= phi <= 180.0
    constraint: -180.0 <= gamma <= 180.0
    constraint: -180.0 <= delta <= 180.0
    h=0, k=0, l=0
    wavelength=1.0
    mu=0, omega=0, chi=0, phi=0, gamma=0, delta=0

Follow on below to learn about more user interface features.

Source Code Documentation
-------------------------

.. automodule :: hklpy2.user
    :members:
    :private-members:
    :show-inheritance:
    :inherited-members:
