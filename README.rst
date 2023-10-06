django-debreach
===============

Extra mitigation against the `BREACH attack <http://breachattack.com/>`_ 
for Django projects. 

Note (that as of version 4.2 Django) includes this protection natively and this 
library is not needed.

django-debreach provides additional protection to Django's built in CSRF
token masking by randomising the content length of each response. This is 
achieved by adding a random string of between 12 and 25 characters as a 
comment to the end of the HTML content. Note that this will only be applied to 
responses with a content type of ``text/html``.

When combined with the built-in mitigations in Django and rate limiting 
(either in your web-server, or by using something like 
`django-ratelimit <http://django-ratelimit.readthedocs.org/>`_), the 
techniques here should provide a fairly comprehensive protection against the 
BREACH attack.

.. image:: https://badge.fury.io/py/django-debreach.png
    :target: https://badge.fury.io/py/django-debreach
    :alt: PyPI
.. image:: https://travis-ci.org/lpomfrey/django-debreach.png?branch=master
    :target: https://travis-ci.org/lpomfrey/django-debreach
    :alt: Build status

.. image:: https://coveralls.io/repos/lpomfrey/django-debreach/badge.png?branch=master
    :target: https://coveralls.io/r/lpomfrey/django-debreach?branch=master
    :alt: Coverage

Installation & Usage
--------------------

Install from PyPI using::

    $ pip install django-debreach

To enable content length modification for all responses, add the
``debreach.middleware.RandomCommentMiddleware`` to the *start* of your
middleware, but *after* the ``GzipMiddleware`` if you are using that.::

    MIDDLEWARE_CLASSES = (
        'debreach.middleware.RandomCommentMiddleware',
        ...
    )

or::

    MIDDLEWARE_CLASSES = (
        'django.middleware.gzip.GzipMiddleware',
        'debreach.middleware.RandomCommentMiddleware',
        ...
    )

If you wish to disable this feature for selected views, simply apply the
``debreach.decorators.random_comment_exempt`` decorator to the view.

If you only want to protect a subset of views with content length modification
then it may be easier to not use the middleware, but to selectively apply the
``debreach.decorators.append_random_comment`` decorator to the views you want
protected.

Python 2 and Django < 2.0 support
---------------------------------

Version 2.0.0 drops all support for Python 2 and Django < 2.0. If you need 
support for those versions continue using ``django-debreach>=1.5.2,<2.0``.
