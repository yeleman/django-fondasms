#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import json
import logging
import traceback

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from fondasms.utils import generic_fondasms_handler

logger = logging.getLogger(__name__)


def fondasms_tester(request):
    ''' display the HTML tester to generate fake events '''
    return render(request, 'fonda_tester.html', {})


@csrf_exempt
def fondasms_handler(request, **options):

    json_str, http_code = generic_fondasms_handler(request.POST, **options)
    return HttpResponse(json_str, status=http_code, mimetype='application/json')
