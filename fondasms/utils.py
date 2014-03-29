#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import datetime
import json
import logging
import traceback

try:
    import pytz
except ImportError:
    pytz = None

logger = logging.getLogger(__name__)
ZERO = datetime.timedelta(0)


class UTC(datetime.tzinfo):
    """
    UTC implementation taken from Python's docs.

    Used only when pytz isn't available.
    """

    def __repr__(self):
        return "<UTC>"

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO

utc = pytz.utc if pytz else UTC()


def import_path(callable_name, module, fallback):
    def do_import(name):
        ''' import a callable from full module.callable name '''
        modname, __, attr = name.rpartition('.')
        if not modname:
            # single module name
            return __import__(attr)
        m = __import__(modname, fromlist=[attr])
        return getattr(m, attr)

    ret = lambda mod, call: do_import('{module}.{callable}'.format(module=mod,
                                                                   callable=call))
    try:
        return ret(module, callable_name)
    except ImportError:
        return ret(fallback, callable_name)


def outgoing_for(to, message, ident=None, priority=0):
    outgoing = {'to': to,
                'message': message}
    if ident is not None:
        outgoing.update({'id': ident})
    if priority:
        outgoing.update({'priority': priority})
    return outgoing


def datetime_from_timestamp(timestamp):
    try:
        return datetime.datetime.utcfromtimestamp(
            int(timestamp) / 1000).replace(tzinfo=utc)
    except (TypeError, ValueError):
        return None
    return None


def generic_fondasms_handler(post_data, **options):
    ''' Received post_data from FondaSMS HTTP requests and process them

        Processing based on module and other options passed
        as kwargs to the view.

        see example in urls.py '''

    stub = 'fondasms.stub'
    mod = options.get('handler_module')
    if options.get('handler_module') is None:
        mod = stub

    # import handlers
    handle_outgoing_request = import_path('handle_outgoing_request', module=mod, fallback=stub)
    handle_incoming_call = import_path('handle_incoming_call', module=mod, fallback=stub)
    handle_incoming_sms = import_path('handle_incoming_sms', module=mod, fallback=stub)
    handle_outgoing_status_change = import_path('handle_outgoing_status_change', module=mod, fallback=stub)
    handle_device_status_change = import_path('handle_device_status_change', module=mod, fallback=stub)
    reply_with_phone_number = import_path('reply_with_phone_number', module=mod, fallback=stub)
    automatic_reply_handler = import_path('automatic_reply_handler', module=mod, fallback=stub)

    action = post_data.get("action")
    handler = lambda x: None
    outgoings = []

    if action == "incoming":
        if post_data.get('message_type') == 'call':
            handler = handle_incoming_call
        if post_data.get('message_type') == 'sms':
            handler = handle_incoming_sms
        outgoings += handle_automatic_reply(payload=post_data,
                                            options=options,
                                            handler=automatic_reply_handler) or []
    elif action == "outgoing":
        handler = handle_outgoing_request
    elif action == 'send_status':
        handler = handle_outgoing_status_change
    elif action == 'device_status':
        handler = handle_device_status_change
    else:
        return json.dumps({}), 200

    try:
        outgoings += handler(post_data) or []
        if not isinstance(outgoings, list):
            outgoings = []
    except Exception as e:
        logger.error("Exception in request processing ({action}) : "
                     "{excp}".format(action=action, excp=e))
        logger.debug("".join(traceback.format_exc()))
        response = {'error': {'message': str(e)}}
        return json.dumps(response), 500

    response = {"events": [],
                "phone_number": reply_with_phone_number(post_data)}
    if len(outgoings):
        response['events'].append({"event": "send",
                            "messages": outgoings})

    return json.dumps(response), 200


def handle_automatic_reply(payload, options, handler=None):

    if not options.get('send_automatic_reply', False):
        return []

    message = None
    if options.get('automatic_reply_via_handler', False):
        message = handler(payload)
    elif len(options.get('automatic_reply_text', '')):
        message = options.get('automatic_reply_text', '-')

    if message:
        return [outgoing_for(to=payload.get('from'),
                             message=message)]

    return []
