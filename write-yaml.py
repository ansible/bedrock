#!/usr/bin/env python

import os

import yaml


def write_images_file():
    data = {
        'docker.io': {
            'images-by-tag-regex': {
                os.environ['IMAGE']: os.environ.get('REGEX', '^.*$'),
            },
        }
    }

    with open('images.yml', 'w') as f:
        yaml.dump(data, stream=f)


if __name__ == '__main__':
    write_images_file()
