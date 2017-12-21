# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import re
import unittest

import django
from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation
from django.http import HttpResponse
from django.test import TestCase
from django.test.client import RequestFactory
from django.utils.crypto import get_random_string
from django.utils.encoding import force_text
from django.views.decorators.csrf import csrf_exempt

from debreach.context_processors import csrf
from debreach.decorators import append_random_comment, random_comment_exempt
from debreach.middleware import CSRFCryptMiddleware, RandomCommentMiddleware


try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse


try:
    unichr
except NameError:
    pass
else:
    chr = unichr


def test_view(request):
    return HttpResponse()


class TestCSRFCryptMiddleware(TestCase):

    if django.VERSION < (1, 10):

        def test_not_encoded(self):
            request = RequestFactory().post(
                '/', {'csrfmiddlewaretoken': 'abc123'}
            )
            middleware = CSRFCryptMiddleware()
            middleware.process_view(request, test_view, (), {})
            self.assertEqual(request.POST.get('csrfmiddlewaretoken'), 'abc123')

        def test_encoded(self):
            request = RequestFactory().post(
                '/',
                {'csrfmiddlewaretoken': 'aBcDeF$ACAAdVd1'}
            )
            middleware = CSRFCryptMiddleware()
            middleware.process_view(request, test_view, (), {})
            self.assertEqual(request.POST.get('csrfmiddlewaretoken'), 'abc123')

        def test_mutable_status(self):
            request = RequestFactory().post(
                '/',
                {'csrfmiddlewaretoken': 'aBcDeF$ACAAdVd1'}
            )
            request.POST._mutable = False
            middleware = CSRFCryptMiddleware()
            middleware.process_view(request, test_view, (), {})
            self.assertFalse(request.POST._mutable)
            request = RequestFactory().post(
                '/',
                {'csrfmiddlewaretoken': 'aBcDeF$ACAAdVd1'}
            )
            request.POST._mutable = True
            middleware = CSRFCryptMiddleware()
            middleware.process_view(request, test_view, (), {})
            self.assertTrue(request.POST._mutable)

        def test_header_not_encoded(self):
            request = RequestFactory().post('/', HTTP_X_CSRFTOKEN='abc123')
            middleware = CSRFCryptMiddleware()
            middleware.process_view(request, test_view, (), {})
            self.assertEqual(request.META.get('HTTP_X_CSRFTOKEN'), 'abc123')

        def test_header_encoded(self):
            request = RequestFactory().post(
                '/', HTTP_X_CSRFTOKEN='aBcDeF$ACAAdVd1',
            )
            middleware = CSRFCryptMiddleware()
            middleware.process_view(request, test_view, (), {})
            self.assertEqual(request.META.get('HTTP_X_CSRFTOKEN'), 'abc123')

        def test_tampering(self):
            request = RequestFactory().post(
                '/', {'csrfmiddlewaretoken': '123456$abc'})
            middleware = CSRFCryptMiddleware()
            with self.assertRaises(SuspiciousOperation):
                middleware.process_view(request, test_view, (), {})

        def test_header_tampering(self):
            request = RequestFactory().post('/', HTTP_X_CSRFTOKEN='123456$abc')
            middleware = CSRFCryptMiddleware()
            with self.assertRaises(SuspiciousOperation):
                middleware.process_view(request, test_view, (), {})

        def test_csrf_exempt(self):
            # This is an odd test. We're testing that, when a view is
            # csrf_exempt, process_view will bail without performing any
            # processing.
            request = RequestFactory().post('/', HTTP_X_CSRFTOKEN="aB$AHM")
            middleware = CSRFCryptMiddleware()
            middleware.process_view(request, csrf_exempt(test_view), (), {})
            self.assertEqual("aB$AHM", request.META['HTTP_X_CSRFTOKEN'])

    else:

        def test_middleware_raises_improperly_configured(self):
            with self.assertRaises(ImproperlyConfigured):
                CSRFCryptMiddleware()


class TestRandomCommentMiddleware(TestCase):

    def test_noop_on_wrong_content_type(self):
        response = HttpResponse('abc', content_type='text/plain')
        request = RequestFactory().get('/')
        middleware = RandomCommentMiddleware()
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

    def test_exemption(self):
        html = '''<html>
    <head><title>Test</title></head>
    <body><p>Test body.</p></body>
</html>'''
        response = HttpResponse(html)
        response._random_comment_exempt = True
        request = RequestFactory().get('/')
        middleware = RandomCommentMiddleware()
        response = middleware.process_response(request, response)
        self.assertEqual(force_text(response.content), html)

    def test_missing_content_type(self):
        request = RequestFactory().get('/')
        response = HttpResponse('')
        del response['Content-Type']
        middleware = RandomCommentMiddleware()
        processed_response = middleware.process_response(request, response)
        self.assertEqual(response, processed_response)

    def test_empty_response_body_ignored(self):
        request = RequestFactory().get('/')
        response = HttpResponse('')
        middleware = RandomCommentMiddleware()
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
        self.assertNotEqual(force_text(response.content), html)
        self.assertIn('<!-- ', force_text(response.content))
        self.assertIn(' -->', force_text(response.content))

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


class TestContextProcessor(TestCase):

    def test_csrf(self):
        request = RequestFactory().get('/')
        request.META['CSRF_COOKIE'] = 'abc123'
        context = csrf(request)
        self.assertTrue(force_text(context['csrf_token']))
        self.assertNotEqual(force_text(context['csrf_token']), 'abc123')

    @unittest.skipUnless(
        django.VERSION < (1, 9),
        'The CSRF token is always present in Django 1.9+'
    )
    def test_no_token_csrf(self):
        request = RequestFactory().get('/')
        context = csrf(request)
        self.assertTrue(force_text(context['csrf_token']))
        self.assertEqual(force_text(context['csrf_token']), 'NOTPROVIDED')


@unittest.skipUnless(
    'test_project' in os.environ.get('DJANGO_SETTINGS_MODULE', ''),
    'Not running in test_project'
)
class IntegrationTests(TestCase):

    def test_adds_comment(self):
        resp = self.client.get(reverse('home'))
        self.assertFalse(resp.content.endswith(b'</html>'))

    if django.VERSION < (1, 10):
        def test_crypt_csrf_token(self):
            resp = self.client.get(reverse('test_form'))
            m = re.search(
                r'value=\'(.*\$.*)\'',
                force_text(resp.content),
                re.MULTILINE | re.DOTALL
            )
            self.assertEqual(len(m.groups()), 1)
            token = m.groups()[0].strip()
            post_resp = self.client.post(
                reverse('test_form'),
                {'csrfmiddlewaretoken': token, 'message': 'Some rubbish'}
            )
            self.assertRedirects(post_resp, reverse('home'))

        def test_crypt_csrf_header(self):
            resp = self.client.get(reverse('test_form'))
            m = re.search(
                r'value=\'(.*\$.*)\'',
                force_text(resp.content),
                re.MULTILINE | re.DOTALL
            )
            self.assertEqual(len(m.groups()), 1)
            token = m.groups()[0].strip()
            post_resp = self.client.post(
                reverse('test_form'),
                {'message': 'Some rubbish'},
                X_CSRFTOKEN=token,
            )
            self.assertRedirects(post_resp, reverse('home'))

        def test_round_trip_loop(self):
            '''
            Checks a wide range of input tokens and keys
            '''
            for _ in range(1000):
                request = RequestFactory().get('/')
                csrf_token = get_random_string(32)
                request.META['CSRF_COOKIE'] = csrf_token
                token = force_text(csrf(request)['csrf_token'])
                request = RequestFactory().post(
                    '/', {'csrfmiddlewaretoken': token})
                middleware = CSRFCryptMiddleware()
                middleware.process_view(request, test_view, (), {})
                self.assertEqual(
                    force_text(request.POST.get('csrfmiddlewaretoken')),
                    force_text(csrf_token)
                )

        def test_round_trip_loop_header(self):
            '''
            Checks a wide range of input tokens and keys
            '''
            for _ in range(1000):
                request = RequestFactory().get('/')
                csrf_token = get_random_string(32)
                request.META['CSRF_COOKIE'] = csrf_token
                token = csrf(request)['csrf_token']
                request = RequestFactory().post(
                    '/',
                    HTTP_X_CSRFTOKEN=force_text(token),
                    HTTP_X_REQUESTED_WITH='XMLHttpRequest'
                )
                middleware = CSRFCryptMiddleware()
                middleware.process_view(request, test_view, (), {})
                self.assertEqual(
                    force_text(request.META.get('HTTP_X_CSRFTOKEN')),
                    force_text(csrf_token)
                )
