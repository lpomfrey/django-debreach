# -*- coding: utf-8 -*-
from __future__ import unicode_literals


try:
    # Django >= 1.4.5
    from django.utils.encoding import force_bytes, force_text, smart_text  # NOQA
    from django.utils.six import string_types, text_type, binary_type  # NOQA
except ImportError:  # pragma: no cover
    # Django < 1.4.5
    from django.utils.encoding import (                         # NOQA
        smart_unicode as smart_text, smart_str as force_bytes,  # NOQA
        force_unicode as force_text)                            # NOQA
    string_types = (basestring,)
    text_type = unicode
    binary_type = str

try:
    # Django >= 1.4
    from django.core.signing import b64_decode, b64_encode  # NOQA
    from django.utils.crypto import get_random_string  # NOQA
except ImportError:  # pragma: no cover
    # Django < 1.4
    import base64
    from random import choice
    get_random_string = lambda n: ''.join(
        [choice('abcdefghijklmnopqrstuvwxyz0123456789') for i in range(n)])
    b64_encode = lambda s: base64.urlsafe_b64encode(s).strip(b'=')
    b64_decode = lambda s: base64.urlsafe_b64decode(s + b'=' * (-len(s) % 4))


def xor(s, pad):
    '''XOR a given string ``s`` with the one-time-pad ``pad``'''
    from itertools import cycle
    s = bytearray(force_bytes(s, encoding='latin-1'))
    pad = bytearray(force_bytes(pad, encoding='latin-1'))
    return binary_type(bytearray(x ^ y for x, y in zip(s, cycle(pad))))
