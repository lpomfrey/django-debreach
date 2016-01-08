# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.signing import b64_encode
from django.middleware.csrf import get_token
from django.utils.crypto import get_random_string
from django.utils.encoding import force_bytes, force_text
from django.utils.functional import lazy
from django.utils.six import text_type

from debreach.utils import xor


def csrf(request):
    """
    Context processor that provides a CSRF token, or the string 'NOTPROVIDED'
    if it has not been provided by either a view decorator or the middleware
    """
    def _get_val():
        token = get_token(request)
        if token is None:
            # In order to be able to provide debugging info in the
            # case of misconfiguration, we use a sentinel value
            # instead of returning an empty dict.
            return 'NOTPROVIDED'
        else:
            token = force_bytes(token, encoding='latin-1')
            key = force_bytes(
                get_random_string(len(token)),
                encoding='latin-1'
            )
            value = b64_encode(xor(token, key))
            return force_text(b'$'.join((key, value)), encoding='latin-1')
    _get_val = lazy(_get_val, text_type)

    return {'csrf_token': _get_val()}
