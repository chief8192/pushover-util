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

import argparse

from push import Push, Priority


def main():

    # Parse the command line arguments into a context.
    parser = argparse.ArgumentParser()
    parser.add_argument("--user_key", dest="user_key", required=True)
    parser.add_argument("--api_token", dest="api_token", required=True)
    parser.add_argument("--message", dest="message", required=True)
    parser.add_argument(
        "--priority",
        dest="priority",
        action="store_true",
        required=False,
        default=False,
    )
    parser.add_argument("--title", dest="title", required=False, default=None)
    context = parser.parse_args()

    priority = Priority.HIGH if context.priority else Priority.NORMAL

    Push(
        context.user_key,
        context.api_token,
        context.message,
        priority=priority,
        title=context.title,
    )


if __name__ == "__main__":
    main()
