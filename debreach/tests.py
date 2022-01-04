# -*- coding: utf-8 -*-
import os
import unittest

from django.http import HttpResponse
from django.test import TestCase
from django.test.client import RequestFactory
from django.urls import reverse
from django.utils.encoding import force_str

from debreach.decorators import append_random_comment, random_comment_exempt
from debreach.middleware import RandomCommentMiddleware


def test_view(request):
    return HttpResponse()


class TestRandomCommentMiddleware(TestCase):

    def test_noop_on_wrong_content_type(self):
        response = HttpResponse('abc', content_type='text/plain')
        request = RequestFactory().get('/')
        middleware = RandomCommentMiddleware(lambda request: response)
        response = middleware.process_response(request, response)
        self.assertEqual(response.content, b'abc')

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
        middleware = RandomCommentMiddleware(lambda request: response)
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
        middleware = RandomCommentMiddleware(lambda request: response)
        response = middleware.process_response(request, response)
        self.assertNotEqual(force_str(response.content), force_str(html))

    def test_exemption(self):
        html = '''<html>
    <head><title>Test</title></head>
    <body><p>Test body.</p></body>
</html>'''
        response = HttpResponse(html)
        response._random_comment_exempt = True
        request = RequestFactory().get('/')
        middleware = RandomCommentMiddleware(lambda request: response)
        response = middleware.process_response(request, response)
        self.assertEqual(force_str(response.content), html)

    def test_missing_content_type(self):
        request = RequestFactory().get('/')
        response = HttpResponse('')
        del response['Content-Type']
        middleware = RandomCommentMiddleware(lambda request: response)
        processed_response = middleware.process_response(request, response)
        self.assertEqual(response, processed_response)

    def test_empty_response_body_ignored(self):
        request = RequestFactory().get('/')
        response = HttpResponse('')
        middleware = RandomCommentMiddleware(lambda request: response)
        processed_response = middleware.process_response(request, response)
        self.assertEqual(len(processed_response.content), 0)


class TestDecorators(TestCase):

    def test_append_random_comment(self):
        html = '''<html>
    <head><title>Test</title></head>
    <body><p>Test body.</p></body>
</html>'''

        @append_random_comment
        def test_view(request):
            return HttpResponse(html)

        request = RequestFactory().get('/')
        response = test_view(request)
        self.assertNotEqual(force_str(response.content), html)
        self.assertIn('<!-- ', force_str(response.content))
        self.assertIn(' -->', force_str(response.content))

    def test_random_comment_exempt(self):
        html = '''<html>
    <head><title>Test</title></head>
    <body><p>Test body.</p></body>
</html>'''

        @random_comment_exempt
        def test_view(request):
            return HttpResponse(html)

        request = RequestFactory().get('/')
        response = test_view(request)
        self.assertTrue(response._random_comment_exempt)


@unittest.skipUnless(
    'test_project' in os.environ.get('DJANGO_SETTINGS_MODULE', ''),
    'Not running in test_project'
)
class IntegrationTests(TestCase):

    def test_adds_comment(self):
        resp = self.client.get(reverse('home'))
        self.assertFalse(resp.content.endswith(b'</html>'))
