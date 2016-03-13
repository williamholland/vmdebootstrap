#! /usr/bin/python
# -*- coding: utf-8 -*-
#
#  lava-submit.py
#
#  Copyright 2015 Neil Williams <codehelp@debian.org>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

"""
Example script - needs configuration (or use lava-tool).
Expects to submit a pipeline job to a QEMU device, so
ensure that the host supports these jobs.
**This script is not to be expanded with argparse or CLI options for
the username, token, hostname or image**.
It is meant to be copied into something like jenkins to do the
submission using hardcoded values, themselves hidden behind a UI.
Other details like architecture, prompt and login information may
need to come from a config file or command line.
LAVA needs a serial console to tell whether the VM booted or not.
Larger images will need the LAVA device to have more memory available.
"""

import os
import yaml
import xmlrpclib

# Constants for each particular script configuration.
USERNAME = ""
TOKEN = ""
HOSTNAME = ""
IMAGE = ""
ARCH = ""
PROMPT = ""
PASSWORD = ""  # leave empty if no root password


def job(image):
    """ Bare bones YAML job definition """
    job_def = {
        'actions': [{
            'deploy': {'images': {'rootfs': {
                'image_arg': "-drive format=raw,file={rootfs}",
                "url": "file://%s" % image
            }},
                'os': 'debian',
                'timeout': {'minutes': 5},
                'to': 'tmpfs'}
        }, {
            'boot': {
                'media': 'tmpfs',
                'prompts': [PROMPT],
                'auto_login': {
                    "login_prompt": "login:",
                    "username": "root"
                },
                'method': 'qemu'}
        }],
        'device_type': 'qemu',
        'job_name': 'vmdebootstrap-test',
        'priority': 'medium',
        "context": {"arch": ARCH},
        'timeouts': {'action': {'minutes': 1}, 'job': {'minutes': 5}},
        'visibility': 'public'}
    if PASSWORD:
        boot = [action['boot'] for action in job_def['actions'] if 'boot' in action][0]
        boot['auto_login'].update({
            "password_prompt": "Password:",
            "password": PASSWORD
        })
    return job_def


def main():
    """ submit using XMLRPC """
    image = os.path.realpath(IMAGE)
    url = "http://%s:%s@%s//RPC2" % (USERNAME, TOKEN, HOSTNAME)
    server = xmlrpclib.ServerProxy(url)
    job_id = server.scheduler.submit_job(yaml.dump(job(image)))
    print job_id
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
