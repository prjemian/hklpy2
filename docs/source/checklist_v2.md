# Feature Checklist for v2

This is a first-cut checklist for the v2 release.
It could be re-organized.

* [ ] user-requested changes
* [ ] move libhkl to be a replaceable back-end computation library
* [ ] easy to save/restore configuration
* [ ] easy to use different *engines*
  * [ ] documentation
  * [ ] example(s)
  * [ ] tests
* Axes
  * [ ] Make it easy to provide additional axes
    * [ ] rotation about arbitrary vector
    * [ ] Solvers with different reciprocal-space axes
    * [ ] extra parameters, as required by solver
  * [ ] user can choose different names for any of the diffractometer axes
* [ ] Default diffractometer geometries
* [ ] Bragg Peak optimization tools
* [ ] Defining orientation matrix or matrices
* [ ] Simulating diffraction and diffractometer modes
* [ ] Built in reciprocal space plans (or scans)
* [ ] Choice of calculation engines other than the hkl C package
* Solver API
  * [ ] a structure (dict or struct) describing a geometry (motors, reference positions, and constraints)
  * [ ] observed mapping between real and reciprocal space to give you the "U" of the UB matrix
  * [ ] the crystallography to give you the "B"
  * [ ] Solver: custom project
  * [ ] Solver: python-wrapped components from `libhkl`
  * [ ] Solver: SPEC
  * [ ] easy to switch between solvers at run time so that new things can be validated
* [ ] [analyzers and polarizers](https://github.com/bluesky/hklpy/issues/92)
* Reflections
  * [ ] [reflection is a Python class](https://github.com/bluesky/hklpy/issues/189)
  * [ ] [`addReflection()`, when to use current positions](https://github.com/bluesky/hklpy/issues/219)
  * [ ] [avoid duplications](https://github.com/bluesky/hklpy/issues/248)
  * [ ] [label each reflection](https://github.com/bluesky/hklpy/issues/293)
  * [ ] [write orientation reflections with scan](https://github.com/bluesky/hklpy/issues/158), 
    [also](https://github.com/bluesky/hklpy/issues/247)
  * [ ] [`cahkl()` should make nice report when reflection can't be reached](https://github.com/bluesky/hklpy/issues/178)
* Other
  * [ ] [modify existing sample](https://github.com/bluesky/hklpy/issues/157)
  * [ ] [control display precision in `wh()` and `pa()`](https://github.com/bluesky/hklpy/issues/179)
  * [ ] [crystallographic *zones*](https://github.com/bluesky/hklpy/issues/291)
* Solvers
  * [ ] `libhkl`
  * [ ] [*ad-hoc* geometries](https://github.com/bluesky/hklpy/issues/244)
  * [ ] [diffcalc](https://github.com/bluesky/hklpy/issues/163)
  * [ ] [TwoC unknown](https://github.com/bluesky/hklpy/issues/165)
  * [ ] [xrayutilities](https://github.com/bluesky/hklpy/issues/162)
  * [ ] SPEC server
* Documentation
  * [ ] How to hold axes fixed during `forward()` transformation
  * [ ] Choosing the default `forward()` solution.
  * [ ] How to migrate from hklpy v1.
