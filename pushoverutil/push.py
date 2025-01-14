#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# MIT License

# Copyright (c) 2025 Matt Doyle

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import datetime
import http.client
import urllib

from enum import Enum
from typing import Optional


MINIMUM_RETRY = 30
MAXIMUM_EXPIRE = 10800


class BadPushoverRequestException(Exception):
    pass


class Priority(Enum):
    LOWEST = -2
    LOW = -1
    NORMAL = 0
    HIGH = 1
    EMERGENCY = 2


def Push(
    user_key: str,
    api_token: str,
    message: str,
    callback: Optional[str] = None,
    devices: Optional[list] = None,
    expire: Optional[int] = None,
    html: Optional[bool] = False,
    priority: Optional[Priority] = Priority.NORMAL,
    retry: Optional[int] = None,
    timestamp: Optional[datetime.datetime] = None,
    title: Optional[str] = None,
    ttl: Optional[int] = None,
    url_title: Optional[str] = None,
    url: Optional[str] = None,
):

    # Emergency priority messages require some additional parameters.
    if priority == Priority.EMERGENCY:
        if not retry or not expire:
            raise BadPushoverRequestException(
                "Emergency priority messages require 'retry' and 'expire' parameters"
            )
        if retry < MINIMUM_RETRY:
            raise BadPushoverRequestException(
                f"The 'retry' parameter must be >= {MINIMUM_RETRY}"
            )
        if expire > MAXIMUM_EXPIRE:
            raise BadPushoverRequestException(
                f"The 'expire' parameter must be <= {MAXIMUM_EXPIRE}"
            )

    parameters = {
        "user": user_key,
        "token": api_token,
        "message": message,
        "callback": callback,
        "device": ",".join(devices) if devices else None,
        "expire": expire,
        "html": int(html),
        "priority": priority.value,
        "retry": retry,
        "timestamp": int(timestamp.timestamp()) if timestamp else None,
        "title": title,
        "ttl": ttl,
        "url_title": url_title,
        "url": url,
    }

    # Filter out any mappings with values left as 'None'.
    parameters = {k: v for k, v in parameters.items() if v is not None}

    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request(
        "POST",
        "/1/messages.json",
        urllib.parse.urlencode(parameters),
        {"Content-type": "application/x-www-form-urlencoded"},
    )
    return conn.getresponse()
