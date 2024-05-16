# Plans for hklpy2

Gather the discussion points, thoughts, issues, etc. for development of
[*hklpy2*](https://github.com/prjemian/hklpy2), the second generation of
the [*hklpy*](https://github.com/bluesky/hklpy) package.

## hklpy release v2.0 project

As stated in the [project](https://github.com/orgs/bluesky/projects/4/settings):

Redesign of the Diffractometer object.

- user-requested changes
- move libhkl to be a replaceable back-end computation library
- easy to save/restore configuration
- easy to use different *engines* (such as `hkl`, `qper_qpar`, `emergence`, ...)

## Backend Solvers as entrypoints

> It provides an useful tool for pluggable Python software development.

[Article with example](https://stackoverflow.com/a/9615473/1046449)
about entrypoints.

Demo (9 years old): https://github.com/RichardBronosky/entrypoint_demo

See the docs in setuptools regarding [*Entry Points for
Plugins*](https://setuptools.pypa.io/en/latest/userguide/entry_point.html#entry-points-for-plugins).
