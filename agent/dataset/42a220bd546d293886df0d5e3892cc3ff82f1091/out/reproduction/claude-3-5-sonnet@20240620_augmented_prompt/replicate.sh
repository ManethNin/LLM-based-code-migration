#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:42a220bd546d293886df0d5e3892cc3ff82f1091-breaking
docker build -t claude-3.5-sonnet-42a220bd546d293886df0d5e3892cc3ff82f1091-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/42a220bd546d293886df0d5e3892cc3ff82f1091/out/reproduction/claude-3-5-sonnet@20240620_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:42a220bd546d293886df0d5e3892cc3ff82f1091-breaking > pre.txt 2>&1
docker run claude-3.5-sonnet-42a220bd546d293886df0d5e3892cc3ff82f1091-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag claude-3.5-sonnet-42a220bd546d293886df0d5e3892cc3ff82f1091-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-42a220bd546d293886df0d5e3892cc3ff82f1091-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-42a220bd546d293886df0d5e3892cc3ff82f1091-reproduction


docker save -o /root/docker-images/claude-3.5-sonnet-42a220bd546d293886df0d5e3892cc3ff82f1091-reproduction.tar claude-3.5-sonnet-42a220bd546d293886df0d5e3892cc3ff82f1091-reproduction
gzip /root/docker-images/claude-3.5-sonnet-42a220bd546d293886df0d5e3892cc3ff82f1091-reproduction.tar