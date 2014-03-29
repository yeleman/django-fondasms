#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

import sys

from flask import Flask

app = Flask('example')

from fondasms.flask_views import fondasms_handler

app.route('/fondasms', methods=['POST'])(fondasms_handler)


def runserver(debug=True):
    http_port = 5000
    app.run(debug=debug, port=http_port, host='0.0.0.0')

if __name__ == '__main__':
    runserver()

