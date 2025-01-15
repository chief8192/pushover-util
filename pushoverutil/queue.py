#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2025 Matt Doyle
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.


import datetime
import functools
import http.client
import os.path
import time
import urllib

from collections import defaultdict
from push import Priority, Push
from threading import Thread, RLock
from typing import Optional


# MAX_COUNTER = 15  # in seconds


def Deduplicate(items):
    seen = set()
    for item in items:
        if item not in seen:
            seen.add(item)
            yield item


class Sender(threading.Thread):
    def __init__(self, initial_messages=None):

        super().__init__()

        self.messages = initial_messages if initial_messages else []
        self.counter = MAX_COUNTER
        self.lock = threading.Lock()

    def EnqueueMessage(self, message):
        with self.lock:
            self.messages.append(message)
            self.counter = MAX_COUNTER

    def DecrementCounter(self):
        with self.lock:
            self.counter -= 1
            return self.counter

    def run(self):

        # Sleep until the countdown is exhausted, which may intermittently be
        # reset by WatchDockerEvents().
        while self.DecrementCounter() > 0:
            time.sleep(1.0)

        # Deduplicate and concatenate all of the accumulated messages.
        with self.lock:
            full_message = "\n".join(Deduplicate(self.messages))
            self.messages.clear()

        # Send full the message out via Pushover.
        Push(full_message, secrets_json_path=self.secrets_json_path)


CLUSTER_DICT = {}


def Push(
    message,
    cluster_key=None,
    high_priority=False,
):

    # Clustering requested, so delay the message in case others arrive.
    if cluster_key:

        sender = CLUSTER_DICT.get(cluster_key)

        # If this cluster hasn't been seen before, or the Sender Thread has
        # already run, start a new Sender.
        if sender is None or not sender.is_alive():
            initial_messages = [message]
            new_sender = Sender(initial_messages=initial_messages)
            CLUSTER_DICT[cluster_key] = new_sender
            new_sender.start()

        # Otherwise, just add the message to the existing Sender.
        else:
            sender.EnqueueMessage(message)

    # No clustering requested, so send the message right away.
    # else:

    # conn = http.client.HTTPSConnection("api.pushover.net:443")
    # conn.request(
    #     "POST",
    #     "/1/messages.json",
    #     urllib.parse.urlencode(
    #         {
    #             "message": message,
    #             "priority": 1 if high_priority else 0,
    #             "token": APP_TOKEN,
    #             "user": USER_KEY,
    #         }
    #     ),
    #     {"Content-type": "application/x-www-form-urlencoded"},
    # )
    # conn.getresponse()


# def PushException(ex, cluster_key=None):
#     Push(ex.__class__.__name__, cluster_key=cluster_key)


class PushoverQueue(Thread):

    def __init__(self, user_key: str, api_token: str, rate_limit: int = 0):
        super().__init__()

        self.user_key = user_key
        self.api_token = api_token
        self.rate_limit = rate_limit  # TODO: is there a pushover limit?

        self.running = False
        self.lock = RLock()
        self.queue = defaultdict(list)

    def Start(self):
        with self.lock:
            self.running = True
            self.start()

    def Stop(self):
        with self.lock:
            self.running = False

    def IsRunning(self):
        with self.lock:
            return self.running

    def run(self):
        while self.IsRunning():
            pass

    def Push(
        self,
        message: str,
        callback: Optional[str] = None,
        clustering_key: Optional[str] = None,
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

        Push(self.user_key, self.api_token, message)
