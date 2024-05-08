"""
Miscellaneous Support.

.. autosummary::

    ~unique_name
"""

import uuid


def unique_name():
    """Short, unique name, first 7 characters of a unique, random uuid."""
    return str(uuid.uuid4())[:7]
