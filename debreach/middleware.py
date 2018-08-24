# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import random

import django
from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation
from django.core.signing import b64_decode
from django.utils.crypto import get_random_string
from django.utils.encoding import force_bytes, force_text
from django.utils.six import binary_type, string_types

from debreach.utils import xor

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    class MiddlewareMixin(object):
        pass


log = logging.getLogger(__name__)


class CSRFCryptMiddleware(object):

    def __init__(self, *args, **kwargs):
        if django.VERSION >= (1, 10):
            raise ImproperlyConfigured(
                "Django 1.10 and above provides it's own CSRF mechanism to "
                "mitigate the BREACH attack, please remove the "
                "{}.{} middleware."
                .format(self.__module__, self.__class__.__name__)
            )

    def _decode(self, token):
        key, value = force_bytes(token, encoding='latin-1').split(b'$', 1)
        return force_text(xor(b64_decode(value), key), encoding='latin-1')

    def process_view(self, request, view, view_args, view_kwargs):
        if getattr(view, 'csrf_exempt', False):
            return None
        if request.POST.get('csrfmiddlewaretoken') \
                and '$' in request.POST.get('csrfmiddlewaretoken'):
            try:
                post_was_mutable = request.POST._mutable
                POST = request.POST.copy()
                token = POST.get('csrfmiddlewaretoken')
                POST['csrfmiddlewaretoken'] = self._decode(token)
                POST._mutable = post_was_mutable
                request.POST = POST
            except:
                log.exception('Error decoding csrfmiddlewaretoken')
                raise SuspiciousOperation(
                    'csrfmiddlewaretoken has been tampered with')
        if request.META.get('HTTP_X_CSRFTOKEN') \
                and '$' in request.META.get('HTTP_X_CSRFTOKEN'):
            try:
                META = request.META.copy()
                token = META.get('HTTP_X_CSRFTOKEN')
                META['HTTP_X_CSRFTOKEN'] = self._decode(token)
                request.META = META
            except:
                log.exception('Error decoding csrfmiddlewaretoken')
                raise SuspiciousOperation(
                    'X-CSRFToken header has been tampered with')
        return None


class RandomCommentMiddleware(MiddlewareMixin):

    def process_response(self, request, response):
        str_types = string_types + (binary_type,)
        if not getattr(response, 'streaming', False) \
                and response.get('Content-Type', '').startswith('text/html') \
                and response.content \
                and isinstance(response.content, str_types) \
                and not getattr(response, '_random_comment_exempt', False) \
                and not getattr(response, '_random_comment_applied', False):
            comment = '<!-- {0} -->'.format(
                get_random_string(random.choice(range(12, 25))))
            response.content = '{0}{1}'.format(
                force_text(response.content), comment)
            response._random_comment_applied = True
            if response.has_header('Content-Length'):
                response['Content-Length'] = str(len(response.content))
        return response
