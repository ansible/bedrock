#!/usr/bin/env python

import os

import yaml


CREDENTIALS = {
    'username': os.environ['DOCKER_USER'],
    'password': os.environ['DOCKER_PASSWORD']
}


def write_images_file():
    data = {
        'docker.io': {
            'credentials': CREDENTIALS,
            'images-by-tag-regex': {
                os.environ['IMAGE']: os.environ['REGEXP'],
            },
        }
    }

    with open('images.yml', 'w') as f:
        yaml.dump(data, stream=f)


if __name__ == '__main__':
    write_images_file()
