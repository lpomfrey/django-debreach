# -*- coding: utf-8 -*-
from __future__ import unicode_literals

try:
    from django.apps import AppConfig
except ImportError:  # pragma: no cover
    class AppConfig(object):
        pass


class DebreachConfig(AppConfig):

    name = 'debreach'
