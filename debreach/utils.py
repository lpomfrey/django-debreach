# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.encoding import force_bytes
from django.utils.six import binary_type


def xor(s, pad):
    '''XOR a given string ``s`` with the one-time-pad ``pad``'''
    from itertools import cycle
    s = bytearray(force_bytes(s, encoding='latin-1'))
    pad = bytearray(force_bytes(pad, encoding='latin-1'))
    return binary_type(bytearray(x ^ y for x, y in zip(s, cycle(pad))))
