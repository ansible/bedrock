#!/usr/bin/env python
"""Sync containers using skopeo."""

import pathlib
import shlex
import subprocess


def main():
    """Main entry point."""
    name = 'skopeo-sync'
    image = 'quay.io/skopeo/stable:v1.7.0'
    sync = [
        'sync',
        '--authfile', '/auth.json',
        '--src', 'yaml',
        '--dest', 'docker',
        '--all',
        '--keep-going',
        '/sync.yml',
        'quay.io/bedrock',
    ]

    try:
        docker('create', '--rm', '-t', '--name', name, image, *sync)
        docker('cp', str(pathlib.Path("auth.json").absolute()), f'{name}:/auth.json')
        docker('cp', str(pathlib.Path("sync.yml").absolute()), f'{name}:/sync.yml')
        docker('start', '--attach', name)
    finally:
        docker('rm', '-f', name)


def docker(*args: str):
    """Run a docker command."""
    cmd = ('docker',) + args
    print(f'==> {shlex.join(cmd)}')
    subprocess.run(cmd, check=True)


if __name__ == '__main__':
    main()
