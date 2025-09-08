#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:42a220bd546d293886df0d5e3892cc3ff82f1091-breaking
docker build -t gemini-1.5-pro-42a220bd546d293886df0d5e3892cc3ff82f1091-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/42a220bd546d293886df0d5e3892cc3ff82f1091/out/reproduction/gemini-1.5-pro-001_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:42a220bd546d293886df0d5e3892cc3ff82f1091-breaking > pre.txt 2>&1
docker run gemini-1.5-pro-42a220bd546d293886df0d5e3892cc3ff82f1091-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag gemini-1.5-pro-42a220bd546d293886df0d5e3892cc3ff82f1091-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:gemini-1.5-pro-42a220bd546d293886df0d5e3892cc3ff82f1091-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:gemini-1.5-pro-42a220bd546d293886df0d5e3892cc3ff82f1091-reproduction


docker save -o /root/docker-images/gemini-1.5-pro-42a220bd546d293886df0d5e3892cc3ff82f1091-reproduction.tar gemini-1.5-pro-42a220bd546d293886df0d5e3892cc3ff82f1091-reproduction
gzip /root/docker-images/gemini-1.5-pro-42a220bd546d293886df0d5e3892cc3ff82f1091-reproduction.tar