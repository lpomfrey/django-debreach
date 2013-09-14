# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from functools import wraps

from django.utils.decorators import decorator_from_middleware, available_attrs

from debreach.middleware import RandomCommentMiddleware


append_random_comment = decorator_from_middleware(RandomCommentMiddleware)


def random_comment_exempt(view_func):
    """
    Makes the random comment middleware ignore the response from the
    decorated view.
    """
    def wrapped_view(*args, **kwargs):
        response = view_func(*args, **kwargs)
        response._random_comment_exempt = True
        return response
    return wraps(view_func, assigned=available_attrs(view_func))(wrapped_view)
