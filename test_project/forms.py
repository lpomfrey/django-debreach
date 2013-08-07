# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms


class TestForm(forms.Form):

    message = forms.CharField()
