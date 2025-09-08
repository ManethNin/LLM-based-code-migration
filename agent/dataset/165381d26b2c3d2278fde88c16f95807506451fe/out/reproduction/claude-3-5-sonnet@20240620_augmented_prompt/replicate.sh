#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:165381d26b2c3d2278fde88c16f95807506451fe-breaking
docker build -t claude-3.5-sonnet-165381d26b2c3d2278fde88c16f95807506451fe-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/165381d26b2c3d2278fde88c16f95807506451fe/out/reproduction/claude-3-5-sonnet@20240620_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:165381d26b2c3d2278fde88c16f95807506451fe-breaking > pre.txt 2>&1
docker run claude-3.5-sonnet-165381d26b2c3d2278fde88c16f95807506451fe-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag claude-3.5-sonnet-165381d26b2c3d2278fde88c16f95807506451fe-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-165381d26b2c3d2278fde88c16f95807506451fe-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-165381d26b2c3d2278fde88c16f95807506451fe-reproduction


docker save -o /root/docker-images/claude-3.5-sonnet-165381d26b2c3d2278fde88c16f95807506451fe-reproduction.tar claude-3.5-sonnet-165381d26b2c3d2278fde88c16f95807506451fe-reproduction
gzip /root/docker-images/claude-3.5-sonnet-165381d26b2c3d2278fde88c16f95807506451fe-reproduction.tar