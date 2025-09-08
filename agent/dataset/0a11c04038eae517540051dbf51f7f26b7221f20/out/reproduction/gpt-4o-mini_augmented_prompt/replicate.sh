#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:0a11c04038eae517540051dbf51f7f26b7221f20-breaking
docker build -t gpt-4o-mini-0a11c04038eae517540051dbf51f7f26b7221f20-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/0a11c04038eae517540051dbf51f7f26b7221f20/out/reproduction/gpt-4o-mini_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:0a11c04038eae517540051dbf51f7f26b7221f20-breaking > pre.txt 2>&1
docker run gpt-4o-mini-0a11c04038eae517540051dbf51f7f26b7221f20-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag gpt-4o-mini-0a11c04038eae517540051dbf51f7f26b7221f20-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:gpt-4o-mini-0a11c04038eae517540051dbf51f7f26b7221f20-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:gpt-4o-mini-0a11c04038eae517540051dbf51f7f26b7221f20-reproduction


docker save -o /root/docker-images/gpt-4o-mini-0a11c04038eae517540051dbf51f7f26b7221f20-reproduction.tar gpt-4o-mini-0a11c04038eae517540051dbf51f7f26b7221f20-reproduction
gzip /root/docker-images/gpt-4o-mini-0a11c04038eae517540051dbf51f7f26b7221f20-reproduction.tar