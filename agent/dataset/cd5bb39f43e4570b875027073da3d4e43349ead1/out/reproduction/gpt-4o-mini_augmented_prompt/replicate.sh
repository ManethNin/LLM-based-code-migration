#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:cd5bb39f43e4570b875027073da3d4e43349ead1-breaking
docker build -t gpt-4o-mini-cd5bb39f43e4570b875027073da3d4e43349ead1-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/cd5bb39f43e4570b875027073da3d4e43349ead1/out/reproduction/gpt-4o-mini_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:cd5bb39f43e4570b875027073da3d4e43349ead1-breaking > pre.txt 2>&1
docker run gpt-4o-mini-cd5bb39f43e4570b875027073da3d4e43349ead1-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag gpt-4o-mini-cd5bb39f43e4570b875027073da3d4e43349ead1-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:gpt-4o-mini-cd5bb39f43e4570b875027073da3d4e43349ead1-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:gpt-4o-mini-cd5bb39f43e4570b875027073da3d4e43349ead1-reproduction


docker save -o /root/docker-images/gpt-4o-mini-cd5bb39f43e4570b875027073da3d4e43349ead1-reproduction.tar gpt-4o-mini-cd5bb39f43e4570b875027073da3d4e43349ead1-reproduction
gzip /root/docker-images/gpt-4o-mini-cd5bb39f43e4570b875027073da3d4e43349ead1-reproduction.tar