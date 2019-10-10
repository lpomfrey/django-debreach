# -*- coding: utf-8 -*-
import logging
import random

from django.utils.crypto import get_random_string
from django.utils.deprecation import MiddlewareMixin
from django.utils.encoding import force_str


log = logging.getLogger(__name__)


class RandomCommentMiddleware(MiddlewareMixin):

    def process_response(self, request, response):
        if not getattr(response, 'streaming', False) \
                and response.get('Content-Type', '').startswith('text/html') \
                and response.content \
                and isinstance(response.content, (bytes, str)) \
                and not getattr(response, '_random_comment_exempt', False) \
                and not getattr(response, '_random_comment_applied', False):
            comment = '<!-- {0} -->'.format(
                get_random_string(random.choice(range(12, 25))))
            response.content = '{0}{1}'.format(
                force_str(response.content), comment)
            response._random_comment_applied = True
            if response.has_header('Content-Length'):
                response['Content-Length'] = str(len(response.content))
        return response
