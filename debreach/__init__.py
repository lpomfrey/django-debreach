# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from distutils import version


__version__ = '1.5.1'
version_info = version.StrictVersion(__version__).version

default_app_config = 'debreach.apps.DebreachConfig'
