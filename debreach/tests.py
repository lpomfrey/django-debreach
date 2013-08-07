# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse
from django.test import TestCase
from django.test.client import RequestFactory
from django.utils.encoding import force_text

from debreach.context_processors import csrf
from debreach.middleware import CSRFCryptMiddleware, RandomCommentMiddleware


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
                'MDEyMzQ1Njc4OWFiY2RlZg==$RKx8XwNfUHtWBD7anBt+ZA=='}
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


class TestContextProcessor(TestCase):

    def test_csrf(self):
        request = RequestFactory().get('/')
        request.META['CSRF_COOKIE'] = 'abc123'
        context = csrf(request)
        self.assertTrue(force_text(context['csrf_token']))
        self.assertNotEqual(force_text(context['csrf_token']), 'abc123')
