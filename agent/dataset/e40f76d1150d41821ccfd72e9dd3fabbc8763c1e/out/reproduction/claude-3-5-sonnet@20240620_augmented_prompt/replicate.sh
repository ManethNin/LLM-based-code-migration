#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:e40f76d1150d41821ccfd72e9dd3fabbc8763c1e-breaking
docker build -t claude-3.5-sonnet-e40f76d1150d41821ccfd72e9dd3fabbc8763c1e-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/e40f76d1150d41821ccfd72e9dd3fabbc8763c1e/out/reproduction/claude-3-5-sonnet@20240620_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:e40f76d1150d41821ccfd72e9dd3fabbc8763c1e-breaking > pre.txt 2>&1
docker run claude-3.5-sonnet-e40f76d1150d41821ccfd72e9dd3fabbc8763c1e-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag claude-3.5-sonnet-e40f76d1150d41821ccfd72e9dd3fabbc8763c1e-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-e40f76d1150d41821ccfd72e9dd3fabbc8763c1e-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-e40f76d1150d41821ccfd72e9dd3fabbc8763c1e-reproduction


docker save -o /root/docker-images/claude-3.5-sonnet-e40f76d1150d41821ccfd72e9dd3fabbc8763c1e-reproduction.tar claude-3.5-sonnet-e40f76d1150d41821ccfd72e9dd3fabbc8763c1e-reproduction
gzip /root/docker-images/claude-3.5-sonnet-e40f76d1150d41821ccfd72e9dd3fabbc8763c1e-reproduction.tar