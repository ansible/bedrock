#!/usr/bin/env python

import argparse
import os
import subprocess
import sys

"""Copy an image from Docker Hub to Quay.io using skopeo. Skopeo can be run from
a container or natively if it is installed. You be logged in to the necessary
regstries or provide the path to a valid auth file.
"""


def validate(image):
    ok = True
    if len(image.split(':')) != 2:
        ok = False
    elif image.split(':')[-1] == '':
        ok = False
    elif '/' in image:
        ok = False
    elif ':/' in image:
        ok = False

    if not ok:
        sys.exit("Invalid format for image. Must be 'image:tag'")


def copy_image(args):
    source_url = 'docker://docker.io/%s' % args.image
    dest_url = 'docker://quay.io/bedrock/%s' % args.image
    command = ['skopeo']
    if args.container:
        skopeo_image = 'quay.io/containers/skopeo:v1.2.0'
        command = [args.container_runtime, 'run', '--rm', '-t']

        if args.authfile:
            command.extend(['-v', '%s:/auth.json:ro' % os.path.abspath(args.authfile)])

        command.append(skopeo_image)

    args = ['copy', '--override-os', 'linux', source_url, dest_url]
    command.extend(args)

    try:
        subprocess.run(command)
    except FileNotFoundError:
        sys.exit("Unable to find executable '%s'." % command[0])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('image', help='Source \'image:tag\' on Docker Hub to be copied to Quay.io')
    parser.add_argument('--container', action='store_true', help='Run using the skopeo container')
    parser.add_argument('--container-runtime', default='docker', choices=['docker', 'podman'], help='Executable used to run containers')
    parser.add_argument('--authfile', help='Path to skopeo auth file')

    args = parser.parse_args()

    validate(args.image)
    copy_image(args)
