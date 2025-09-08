#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:dbdc7d2c4a28a8d65edcd0cdece91c0bc357b869-breaking
docker build -t claude-3.5-sonnet-dbdc7d2c4a28a8d65edcd0cdece91c0bc357b869-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/dbdc7d2c4a28a8d65edcd0cdece91c0bc357b869/out/reproduction/claude-3-5-sonnet@20240620_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:dbdc7d2c4a28a8d65edcd0cdece91c0bc357b869-breaking > pre.txt 2>&1
docker run claude-3.5-sonnet-dbdc7d2c4a28a8d65edcd0cdece91c0bc357b869-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag claude-3.5-sonnet-dbdc7d2c4a28a8d65edcd0cdece91c0bc357b869-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-dbdc7d2c4a28a8d65edcd0cdece91c0bc357b869-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-dbdc7d2c4a28a8d65edcd0cdece91c0bc357b869-reproduction


docker save -o /root/docker-images/claude-3.5-sonnet-dbdc7d2c4a28a8d65edcd0cdece91c0bc357b869-reproduction.tar claude-3.5-sonnet-dbdc7d2c4a28a8d65edcd0cdece91c0bc357b869-reproduction
gzip /root/docker-images/claude-3.5-sonnet-dbdc7d2c4a28a8d65edcd0cdece91c0bc357b869-reproduction.tar