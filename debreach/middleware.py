# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
import logging
import random
from Crypto.Cipher import AES

from django.core.exceptions import SuspiciousOperation
from django.utils import six
from django.utils.crypto import get_random_string
from django.utils.encoding import force_bytes

log = logging.getLogger(__name__)


class CSRFCryptMiddleware(object):

    def process_request(self, request):
        if request.POST.get('csrfmiddlewaretoken') \
                and '$' in request.POST.get('csrfmiddlewaretoken'):
            try:
                POST = request.POST.copy()
                token = POST.get('csrfmiddlewaretoken')
                key, value = token.split('$')
                key = base64.decodestring(force_bytes(key)).strip()
                value = base64.decodestring(force_bytes(value)).strip()
                aes = AES.new(key)
                POST['csrfmiddlewaretoken'] = aes.decrypt(value).strip()
                POST._mutable = False
                request.POST = POST
            except:
                import traceback
                traceback.print_exc()
                log.exception('Error decoding csrfmiddlewaretoken')
                raise SuspiciousOperation(
                    'csrfmiddlewaretoken has been tampered with')
            return


class RandomCommentMiddleware(object):

    def process_response(self, request, response):
        if not getattr(response, 'streaming', False) \
                and response['Content-Type'] == 'text/html' \
                and isinstance(response.content, six.string_types):
            comment = '<!-- {0} -->'.format(
                get_random_string(random.choice(range(12, 25))))
            response.content = '{0}{1}'.format(response.content, comment)
        return response
