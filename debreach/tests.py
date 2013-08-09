# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import re

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.test import TestCase
from django.test.client import RequestFactory
from django.utils.unittest import skipUnless

from debreach.compat import force_text
from debreach.context_processors import csrf
from debreach.middleware import CSRFCryptMiddleware, RandomCommentMiddleware

try:
    unichr
except NameError:
    pass
else:
    chr = unichr


class TestCSRFCryptMiddleware(TestCase):

    def test_not_encoded(self):
        request = RequestFactory().post('/', {'csrfmiddlewaretoken': 'abc123'})
        middleware = CSRFCryptMiddleware()
        middleware.process_request(request)
        self.assertEqual(request.POST.get('csrfmiddlewaretoken'), 'abc123')

    def test_encoded(self):
        request = RequestFactory().post(
            '/',
            {'csrfmiddlewaretoken':
                'Ump3NGw2b0t1R1J5VlZiOQ==$sBDBSs99N2pbyLVHloLaLg=='}
        )
        middleware = CSRFCryptMiddleware()
        middleware.process_request(request)
        self.assertEqual(request.POST.get('csrfmiddlewaretoken'), 'abc123')


class TestRandomCommentMiddleware(TestCase):

    def test_noop_on_wrong_content_type(self):
        response = HttpResponse('abc', content_type='text/plain')
        request = RequestFactory().get('/')
        middleware = RandomCommentMiddleware()
        response = middleware.process_response(request, response)
        self.assertEqual(response.content, 'abc')

    def test_html_content_type(self):
        html = '''<!doctype html>
<html>
    <head>
        <title>Page title</title>
    </head>
    <body>
        <h1>Test</h1>
        <p>Lorem ipsum</p>
    </body>
</html>'''
        response = HttpResponse(html, content_type='text/html')
        request = RequestFactory().get('/')
        middleware = RandomCommentMiddleware()
        response = middleware.process_response(request, response)
        self.assertNotEqual(response.content, html)

    def test_unicode_characters(self):
        html = '''<!doctype html>
<html>
    <head>
        <title>Page title</title>
    </head>
    <body>
        <h1>Test</h1>
        <p>{0}</p>
    </body>
</html>'''.format(''.join(chr(x) for x in range(9999)))
        response = HttpResponse(html, content_type='text/html')
        request = RequestFactory().get('/')
        middleware = RandomCommentMiddleware()
        response = middleware.process_response(request, response)
        self.assertNotEqual(force_text(response.content), force_text(html))


class TestContextProcessor(TestCase):

    def test_csrf(self):
        request = RequestFactory().get('/')
        request.META['CSRF_COOKIE'] = 'abc123'
        context = csrf(request)
        self.assertTrue(force_text(context['csrf_token']))
        self.assertNotEqual(force_text(context['csrf_token']), 'abc123')


@skipUnless(
    'test_project' in os.environ.get('DJANGO_SETTINGS_MODULE', ''),
    'Not running in test_project'
)
class IntegrationTests(TestCase):

    def test_adds_comment(self):
        resp = self.client.get(reverse('home'))
        self.assertFalse(resp.content.endswith('</html>'))

    def test_crypt_csrf_token(self):
        resp = self.client.get(reverse('test_form'))
        m = re.search(
            r'value=\'(.*\$.*)\'', resp.content, re.MULTILINE | re.DOTALL)
        self.assertEqual(len(m.groups()), 1)
        token = m.groups()[0].strip()
        post_resp = self.client.post(
            reverse('test_form'),
            {'csrfmiddlewaretoken': token, 'message': 'Some rubbish'}
        )
        self.assertRedirects(post_resp, reverse('home'))
