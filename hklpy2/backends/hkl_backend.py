"""
Backend: Hkl

:home: https://people.debian.org/~picca/hkl/hkl.html
:source: https://repo.or.cz/hkl.git
"""

import gi

gi.require_version("Hkl", "5.0")

from gi.repository import Hkl as libhkl  # noqa: E402

__version__ = libhkl.VERSION
