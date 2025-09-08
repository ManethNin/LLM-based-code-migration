#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:e40f76d1150d41821ccfd72e9dd3fabbc8763c1e-breaking
docker build -t gpt-4o-e40f76d1150d41821ccfd72e9dd3fabbc8763c1e-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/e40f76d1150d41821ccfd72e9dd3fabbc8763c1e/out/reproduction/gpt-4o_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:e40f76d1150d41821ccfd72e9dd3fabbc8763c1e-breaking > pre.txt 2>&1
docker run gpt-4o-e40f76d1150d41821ccfd72e9dd3fabbc8763c1e-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag gpt-4o-e40f76d1150d41821ccfd72e9dd3fabbc8763c1e-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:gpt-4o-e40f76d1150d41821ccfd72e9dd3fabbc8763c1e-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:gpt-4o-e40f76d1150d41821ccfd72e9dd3fabbc8763c1e-reproduction


docker save -o /root/docker-images/gpt-4o-e40f76d1150d41821ccfd72e9dd3fabbc8763c1e-reproduction.tar gpt-4o-e40f76d1150d41821ccfd72e9dd3fabbc8763c1e-reproduction
gzip /root/docker-images/gpt-4o-e40f76d1150d41821ccfd72e9dd3fabbc8763c1e-reproduction.tar