#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:3a4a2b11483689ca3e99e92785a7b27c56d072b8-breaking
docker build -t gpt-4o-3a4a2b11483689ca3e99e92785a7b27c56d072b8-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/3a4a2b11483689ca3e99e92785a7b27c56d072b8/out/reproduction/gpt-4o_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:3a4a2b11483689ca3e99e92785a7b27c56d072b8-breaking > pre.txt 2>&1
docker run gpt-4o-3a4a2b11483689ca3e99e92785a7b27c56d072b8-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag gpt-4o-3a4a2b11483689ca3e99e92785a7b27c56d072b8-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:gpt-4o-3a4a2b11483689ca3e99e92785a7b27c56d072b8-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:gpt-4o-3a4a2b11483689ca3e99e92785a7b27c56d072b8-reproduction


docker save -o /root/docker-images/gpt-4o-3a4a2b11483689ca3e99e92785a7b27c56d072b8-reproduction.tar gpt-4o-3a4a2b11483689ca3e99e92785a7b27c56d072b8-reproduction
gzip /root/docker-images/gpt-4o-3a4a2b11483689ca3e99e92785a7b27c56d072b8-reproduction.tar