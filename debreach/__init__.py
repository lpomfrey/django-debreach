# -*- coding: utf-8 -*-
import packaging.version


__version__ = '2.1.0'
version_info = packaging.version.Version(__version__).release

default_app_config = 'debreach.apps.DebreachConfig'
