# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys


os.environ['PYTHONPATH'] = os.path.dirname(__file__)
os.environ['DJANGO_SETTINGS_MODULE'] = 'test_project.settings'


def runtests():
    from django.conf import settings
    from django.test.utils import get_runner
    test_runner = get_runner(settings)()
    failures = test_runner.run_tests(['debreach'])
    sys.exit(failures)


if __name__ == '__main__':
    runtests()
