#!/usr/bin/env python

import json
import os

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

with open('auth.json', 'w') as f:
    json.dump(data, f, indent=4)
