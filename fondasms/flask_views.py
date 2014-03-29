#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import json
import logging
import traceback

from flask import render_template, request, Response

from fondasms.utils import generic_fondasms_handler

logger = logging.getLogger(__name__)


def fondasms_handler(**options):

    print(options)

    json_str, http_code = generic_fondasms_handler(request.form, **options)
    return Response(response=json_str,
                    status=http_code,
                    mimetype="application/json")



def fondasms_tester():
    return render_template('fonda_tester.html')
