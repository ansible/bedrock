#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
"""Sync containers using skopeo."""
from __future__ import annotations

import argparse
import dataclasses
import json
import os
import re
import secrets
import shlex
import subprocess
import tempfile
import types

import yaml

argcomplete: types.ModuleType | None

try:
    import argcomplete
except ImportError:
    argcomplete = None


AUTH_PATH = '/auth.json'
SYNC_PATH = '/sync.yml'


def main() -> None:
    """Main entry point."""
    args = parse_args()
    source = Repository.parse(args.source)
    destination = Repository.parse(args.destination)
    tags = get_tags(source)

    if args.match:
        pattern = re.compile(args.match)
        tags = list(filter(pattern.search, tags))

    if args.list:
        print('\n'.join(tags))
        return

    sync_repository(source, destination, tags)


def sync_repository(source: Repository, destination: Repository, tags: list[str]) -> None:
    """Sync the specified tags from the source to the destination repository."""
    sync = [
        'sync',
        '--src', 'yaml',
        '--dest', 'docker',
        '--authfile', AUTH_PATH,
        '--all',
        '--preserve-digests',
        '--keep-going',
        SYNC_PATH,
        str(destination),
    ]

    with tempfile.NamedTemporaryFile(prefix='sync-', suffix='.yml') as sync_file:
        write_sync_yaml(sync_file.name, source, tags)
        files = {sync_file.name: SYNC_PATH}
        skopeo(*sync, files=files)


def parse_args() -> CliArgs:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', help='source repository')
    parser.add_argument('destination', help='destination organization')
    parser.add_argument('--match', help='tag regex to match')
    parser.add_argument('--list', action='store_true', help='list source tags without syncing')

    if argcomplete:
        argcomplete.autocomplete(parser)

    parsed_args = parser.parse_args()
    kwargs = {field.name: getattr(parsed_args, field.name) for field in dataclasses.fields(CliArgs)}
    args = CliArgs(**kwargs)

    return args


@dataclasses.dataclass(frozen=True)
class CliArgs:
    """Command line arguments."""
    source: str
    destination: str
    match: str | None
    list: bool


@dataclasses.dataclass(frozen=True)
class Repository:
    """Container repository."""
    registry: str
    name: str

    def __str__(self):
        return f'{self.registry}/{self.name}'

    @staticmethod
    def parse(value: str) -> Repository:
        """Parse the value as a container repository and return a Repository instance."""
        registry, name = value.split('/', 1)

        return Repository(
            registry=registry,
            name=name,
        )


def skopeo(*args: str, files: dict[str, str] | None = None, capture_output=False) -> subprocess.CompletedProcess:
    """Run the specified skopeo command and return the result."""
    container_name = f'skopeo-{secrets.token_hex(4)}'
    image = 'quay.io/skopeo/stable:v1.11'
    files = (files or {}).copy()

    with tempfile.NamedTemporaryFile(prefix='auth-', suffix='.json') as auth_file:
        write_auth_file(auth_file.name)

        files[auth_file.name] = AUTH_PATH

        try:
            docker('create', '-t', '--name', container_name, image, *args)

            for src, dst in files.items():
                docker('cp', src, f'{container_name}:{dst}')

            return docker('start', '--attach', container_name, capture_output=capture_output)
        finally:
            docker('rm', '-f', container_name)


def write_sync_yaml(path: str, repository: Repository, tags: list[str]) -> None:
    """Write a skopeo sync YAML configuration file."""
    data = {
        repository.registry: dict(
            images={
                repository.name: tags,
            },
        ),
    }

    with open(path, 'w') as sync_file:
        yaml.dump(data, stream=sync_file)


def write_auth_file(path: str):
    data = {
        "auths": {
            "docker.io": {
                "auth": os.environ['DOCKER_TOKEN']
            },
            "quay.io": {
                "auth": os.environ['QUAY_TOKEN']
            }
        }
    }

    with open(path, 'w') as auth_file:
        json.dump(data, auth_file, indent=4)


def get_tags(repository: Repository) -> list[str]:
    """Return a list of tags from the specified repository."""
    inspect = [
        'inspect',
        '--authfile', AUTH_PATH,
        f'docker://{repository}',
    ]

    return json.loads(skopeo(*inspect, capture_output=True).stdout)['RepoTags']


def docker(*args: str, capture_output=False) -> subprocess.CompletedProcess:
    """Run a docker command."""
    cmd = ('docker',) + args
    print(f'==> {shlex.join(cmd)}', flush=True)
    return subprocess.run(cmd, check=True, capture_output=capture_output)


if __name__ == '__main__':
    main()
