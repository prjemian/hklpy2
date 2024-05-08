"""
Miscellaneous Support.

.. autosummary::

    ~unique_name
"""

import uuid


def unique_name(prefix=""):
    """Short, unique name, first 7 characters of a unique, random uuid."""
    return prefix + str(uuid.uuid4())[:7]
