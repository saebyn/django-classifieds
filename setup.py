# vim: set fileencoding=utf-8 ft=python ff=unix nowrap tabstop=4 shiftwidth=4 softtabstop=4 smarttab shiftround expandtab :
"""
distutils setup.py file.

"""

from distutils.core import setup
import re


# From http://stackoverflow.com/a/7071358/123383
VERSIONFILE="classifieds/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))


setup(
    name = 'django-classifieds',
    version = verstr,
    description = 'A Django app for classified ad creation, payment, management, viewing, and searching.',

    long_description = open('README.rst').read(),
    packages = ['classifieds'],

    maintainer = 'John Weaver',
    maintainer_email = 'john@saebyn.info',
)
