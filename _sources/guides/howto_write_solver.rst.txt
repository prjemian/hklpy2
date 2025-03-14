.. _howto.solvers.write:

How to write a new Solver
-------------------------

.. caution:: TODO:: work-in-progress

Until this document is written, review the existing solvers:

* :class:`~hklpy2.backends.hkl_soleil.HklSolver`
* :class:`~hklpy2.backends.no_op.NoOpSolver`
* :class:`~hklpy2.backends.th_tth_q.ThTthSolver`

## SolverBase

|solver| classes always subclass :class:`~hklpy2.backends.base.SolverBase`::

    from hklpy2.backends.SolverBase

    class MySolver(SolverBase):
        ...

.. TODO: Collected considerations for Solvers
    - https://github.com/bluesky/hklpy/issues/14
    - https://github.com/bluesky/hklpy/issues/161
    - https://github.com/bluesky/hklpy/issues/162
    - https://github.com/bluesky/hklpy/issues/163
    - https://github.com/bluesky/hklpy/issues/165
    - https://github.com/bluesky/hklpy/issues/244
    - https://xrayutilities.sourceforge.io/
    - https://cohere.readthedocs.io
    - https://github.com/AdvancedPhotonSource/cohere-scripts/tree/main/scripts/beamlines/aps_34idc
    - https://xrayutilities.sourceforge.io/_modules/xrayutilities/experiment.html#QConversion
    - https://github.com/DiamondLightSource/diffcalc
    - SPEC server mode
    - https://github.com/prjemian/pyub
