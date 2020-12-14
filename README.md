# bedrock
Infrastructure for mirroring Docker Hub base images on quay.io using skopeo.

### Manual Copy

To manually copy a specific image from Docker Hub to Quay.io:

```
export DOCKER_TOKEN=[docker token]
export QUAY_TOKEN=[quay token]

./write-auth.py
./manual-copy --authfile auth.json [image:tag]
```
