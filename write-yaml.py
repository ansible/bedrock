#!/usr/bin/env python

import os
import sys

import yaml

IMAGE_FILES = {
    'python2': {
        'python': r'^2\.[6-7](\.[0-9]+)?$',
    },
    'python3': {
        'python': r'^3\.[6-9](\.[0-9]+)?$',
    },
    'golang': {
        'golang': r'^1\.1[1-9]((\.[0-9]+)-alpine[0-9]+\.[0-9]+)?$',
    },
}

CREDENTIALS = {
    'username': os.environ['DOCKER_USER'],
    'password': os.environ['DOCKER_PASSWORD']
}


def write_images_file(file):
    data = {
        'docker.io': {
            'credentials': CREDENTIALS,
            'images-by-tag-regex': IMAGE_FILES[file],
        }
    }

    with open('%s.yml' % file, 'w') as f:
        yaml.dump(data, stream=f)


if __name__ == '__main__':
    file = sys.argv[1]
    write_images_file(file)
