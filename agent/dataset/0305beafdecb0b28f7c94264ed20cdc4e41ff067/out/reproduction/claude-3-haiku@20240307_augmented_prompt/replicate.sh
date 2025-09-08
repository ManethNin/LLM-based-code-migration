#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:0305beafdecb0b28f7c94264ed20cdc4e41ff067-breaking
docker build -t claude-3-haiku-0305beafdecb0b28f7c94264ed20cdc4e41ff067-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/0305beafdecb0b28f7c94264ed20cdc4e41ff067/out/reproduction/claude-3-haiku@20240307_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:0305beafdecb0b28f7c94264ed20cdc4e41ff067-breaking > pre.txt 2>&1
docker run claude-3-haiku-0305beafdecb0b28f7c94264ed20cdc4e41ff067-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag claude-3-haiku-0305beafdecb0b28f7c94264ed20cdc4e41ff067-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:claude-3-haiku-0305beafdecb0b28f7c94264ed20cdc4e41ff067-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:claude-3-haiku-0305beafdecb0b28f7c94264ed20cdc4e41ff067-reproduction


docker save -o /root/docker-images/claude-3-haiku-0305beafdecb0b28f7c94264ed20cdc4e41ff067-reproduction.tar claude-3-haiku-0305beafdecb0b28f7c94264ed20cdc4e41ff067-reproduction
gzip /root/docker-images/claude-3-haiku-0305beafdecb0b28f7c94264ed20cdc4e41ff067-reproduction.tar