# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import re_path
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from test_project.forms import TestForm

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
    # Examples:
    # url(r'^$', 'test_project.views.home', name='home'),
    # url(r'^test_project/', include('test_project.foo.urls')),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    re_path(r"^$", TemplateView.as_view(template_name="home.html"), name="home"),
    re_path(
        r"^form/$",
        FormView.as_view(
            form_class=TestForm, template_name="test.html", success_url="/"
        ),
        name="test_form",
    ),
]
