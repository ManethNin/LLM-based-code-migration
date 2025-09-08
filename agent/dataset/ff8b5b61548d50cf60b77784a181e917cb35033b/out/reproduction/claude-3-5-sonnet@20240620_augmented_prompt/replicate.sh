#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:ff8b5b61548d50cf60b77784a181e917cb35033b-breaking
docker build -t claude-3.5-sonnet-ff8b5b61548d50cf60b77784a181e917cb35033b-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/ff8b5b61548d50cf60b77784a181e917cb35033b/out/reproduction/claude-3-5-sonnet@20240620_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:ff8b5b61548d50cf60b77784a181e917cb35033b-breaking > pre.txt 2>&1
docker run claude-3.5-sonnet-ff8b5b61548d50cf60b77784a181e917cb35033b-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag claude-3.5-sonnet-ff8b5b61548d50cf60b77784a181e917cb35033b-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-ff8b5b61548d50cf60b77784a181e917cb35033b-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-ff8b5b61548d50cf60b77784a181e917cb35033b-reproduction


docker save -o /root/docker-images/claude-3.5-sonnet-ff8b5b61548d50cf60b77784a181e917cb35033b-reproduction.tar claude-3.5-sonnet-ff8b5b61548d50cf60b77784a181e917cb35033b-reproduction
gzip /root/docker-images/claude-3.5-sonnet-ff8b5b61548d50cf60b77784a181e917cb35033b-reproduction.tar