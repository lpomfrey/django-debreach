#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
from setuptools import setup, find_packages


def get_version(package):
    '''
    Return package version as listed in `__version__` in `init.py`.
    '''
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search(
        '^__version__ = [\'"]([^\'"]+)[\'"]', init_py, re.MULTILINE
    ).group(1)


version = get_version('debreach')


_PUBLISH_WARNING = '''
******************
!!! DEPRECATED !!!
******************

Use twine to publish packages to pypi now.

Ensure you have the `wheel` and `twine` packages installed with

    pip install wheel twine

Then create some distributions like

    python setup.py sdist bdist_wheel

Then upload with twine

    twine upload dist/*
'''

if sys.argv[-1] == 'publish':
    print(_PUBLISH_WARNING)
    sys.exit()


setup(
    name='django-debreach',
    version=version,
    url='http://github.com/lpomfrey/django-debreach',
    license='BSD',
    description='Adds middleware and context processors to give some '
                'protection against the BREACH attack in Django.',
    author='Luke Pomfrey',
    author_email='lpomfrey@gmail.com',
    packages=find_packages(exclude=('test_project', 'docs')),
    install_requires=[],
    tests_require=[
        'django',
    ],
    test_suite='runtests.runtests',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: WWW/HTTP'
    ]
)
