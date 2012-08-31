# vim: set fileencoding=utf-8 ft=python ff=unix nowrap tabstop=4 shiftwidth=4 softtabstop=4 smarttab shiftround expandtab :
"""
django-classifieds package
"""

from _version import __version__


VERSION = __version__
__version_info__ = tuple([ int(num) for num in __version__.split('.')])
