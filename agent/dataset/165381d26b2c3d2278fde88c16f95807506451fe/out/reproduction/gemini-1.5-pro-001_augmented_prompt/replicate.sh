#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:165381d26b2c3d2278fde88c16f95807506451fe-breaking
docker build -t gemini-1.5-pro-165381d26b2c3d2278fde88c16f95807506451fe-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/165381d26b2c3d2278fde88c16f95807506451fe/out/reproduction/gemini-1.5-pro-001_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:165381d26b2c3d2278fde88c16f95807506451fe-breaking > pre.txt 2>&1
docker run gemini-1.5-pro-165381d26b2c3d2278fde88c16f95807506451fe-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag gemini-1.5-pro-165381d26b2c3d2278fde88c16f95807506451fe-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:gemini-1.5-pro-165381d26b2c3d2278fde88c16f95807506451fe-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:gemini-1.5-pro-165381d26b2c3d2278fde88c16f95807506451fe-reproduction


docker save -o /root/docker-images/gemini-1.5-pro-165381d26b2c3d2278fde88c16f95807506451fe-reproduction.tar gemini-1.5-pro-165381d26b2c3d2278fde88c16f95807506451fe-reproduction
gzip /root/docker-images/gemini-1.5-pro-165381d26b2c3d2278fde88c16f95807506451fe-reproduction.tar