# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from functools import wraps

import django
from django.utils.decorators import available_attrs, decorator_from_middleware

from debreach.middleware import CSRFCryptMiddleware, RandomCommentMiddleware


append_random_comment = decorator_from_middleware(RandomCommentMiddleware)
append_random_comment.__name__ = str('append_random_comment')
append_random_comment.__doc__ = '''
Applies a random comment to the response of the decorated view in the same
way as the RandomCommentMiddleware. Using both, or using the decorator
multiple times is harmless and efficient.
'''


def random_comment_exempt(view_func):
    """
    Marks a view as being exempt from having its response modified by the
    RandomCommentMiddleware
    """
    def wrapped_view(*args, **kwargs):
        response = view_func(*args, **kwargs)
        response._random_comment_exempt = True
        return response
    return wraps(view_func, assigned=available_attrs(view_func))(wrapped_view)


if django.VERSION < (1, 10):
    csrf_decrypt = decorator_from_middleware(CSRFCryptMiddleware)
    append_random_comment.__name__ = str('append_random_comment')
    append_random_comment.__doc__ = '''
    Performs the function of the CSRFCryptMiddleware, xor-ing the crypted CSRF
    token back into its original form. Using both, or using the decorator
    multiple times is harmless and efficient.
    '''
