# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
from Crypto.Cipher import AES

from django.middleware.csrf import get_token
from django.utils.functional import lazy

from debreach.compat import \
    get_random_string, text_type, force_bytes, force_text


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
            key = force_bytes(get_random_string(16))
            aes = AES.new(key)
            pad_length = 16 - (len(token) % 16 or 16)
            padding = ''.join('#' for _ in range(pad_length))
            value = base64.b64encode(
                aes.encrypt('{0}{1}'.format(token, padding))
            )
            token = '$'.join((force_text(key), force_text(value)))
            return force_text(token)
    _get_val = lazy(_get_val, text_type)

    return {'csrf_token': _get_val()}
