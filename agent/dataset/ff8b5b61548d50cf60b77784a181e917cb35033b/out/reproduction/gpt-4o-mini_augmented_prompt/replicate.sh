#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:ff8b5b61548d50cf60b77784a181e917cb35033b-breaking
docker build -t gpt-4o-mini-ff8b5b61548d50cf60b77784a181e917cb35033b-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/ff8b5b61548d50cf60b77784a181e917cb35033b/out/reproduction/gpt-4o-mini_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:ff8b5b61548d50cf60b77784a181e917cb35033b-breaking > pre.txt 2>&1
docker run gpt-4o-mini-ff8b5b61548d50cf60b77784a181e917cb35033b-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag gpt-4o-mini-ff8b5b61548d50cf60b77784a181e917cb35033b-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:gpt-4o-mini-ff8b5b61548d50cf60b77784a181e917cb35033b-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:gpt-4o-mini-ff8b5b61548d50cf60b77784a181e917cb35033b-reproduction


docker save -o /root/docker-images/gpt-4o-mini-ff8b5b61548d50cf60b77784a181e917cb35033b-reproduction.tar gpt-4o-mini-ff8b5b61548d50cf60b77784a181e917cb35033b-reproduction
gzip /root/docker-images/gpt-4o-mini-ff8b5b61548d50cf60b77784a181e917cb35033b-reproduction.tar