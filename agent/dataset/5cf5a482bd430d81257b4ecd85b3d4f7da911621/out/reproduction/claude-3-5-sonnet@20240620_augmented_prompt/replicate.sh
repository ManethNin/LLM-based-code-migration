#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:5cf5a482bd430d81257b4ecd85b3d4f7da911621-breaking
docker build -t claude-3.5-sonnet-5cf5a482bd430d81257b4ecd85b3d4f7da911621-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/5cf5a482bd430d81257b4ecd85b3d4f7da911621/out/reproduction/claude-3-5-sonnet@20240620_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:5cf5a482bd430d81257b4ecd85b3d4f7da911621-breaking > pre.txt 2>&1
docker run claude-3.5-sonnet-5cf5a482bd430d81257b4ecd85b3d4f7da911621-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag claude-3.5-sonnet-5cf5a482bd430d81257b4ecd85b3d4f7da911621-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-5cf5a482bd430d81257b4ecd85b3d4f7da911621-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-5cf5a482bd430d81257b4ecd85b3d4f7da911621-reproduction


docker save -o /root/docker-images/claude-3.5-sonnet-5cf5a482bd430d81257b4ecd85b3d4f7da911621-reproduction.tar claude-3.5-sonnet-5cf5a482bd430d81257b4ecd85b3d4f7da911621-reproduction
gzip /root/docker-images/claude-3.5-sonnet-5cf5a482bd430d81257b4ecd85b3d4f7da911621-reproduction.tar