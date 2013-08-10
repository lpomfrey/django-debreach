# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
from Crypto.Cipher import AES

from django.middleware.csrf import get_token
from django.utils.functional import lazy

from debreach.compat import get_random_string, smart_text, text_type


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
            key = get_random_string(16)
            aes = AES.new(key)
            padding = ''.join(' ' for x in range(16 - (len(token) % 16)))
            value = base64.encodestring(
                aes.encrypt('{0}{1}'.format(token, padding))).strip()
            token = '$'.join((key, value))
            return smart_text(token)
    _get_val = lazy(_get_val, text_type)

    return {'csrf_token': _get_val()}
