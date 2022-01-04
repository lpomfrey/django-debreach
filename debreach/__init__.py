# -*- coding: utf-8 -*-
from distutils import version


__version__ = '2.1.0'
version_info = version.StrictVersion(__version__).version

default_app_config = 'debreach.apps.DebreachConfig'
