#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:06c5386831e97e94d9b9fd155d3ea4aa8711c4e7-breaking
docker build -t claude-3.5-sonnet-06c5386831e97e94d9b9fd155d3ea4aa8711c4e7-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/06c5386831e97e94d9b9fd155d3ea4aa8711c4e7/out/reproduction/claude-3-5-sonnet@20240620_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:06c5386831e97e94d9b9fd155d3ea4aa8711c4e7-breaking > pre.txt 2>&1
docker run claude-3.5-sonnet-06c5386831e97e94d9b9fd155d3ea4aa8711c4e7-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag claude-3.5-sonnet-06c5386831e97e94d9b9fd155d3ea4aa8711c4e7-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-06c5386831e97e94d9b9fd155d3ea4aa8711c4e7-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-06c5386831e97e94d9b9fd155d3ea4aa8711c4e7-reproduction


docker save -o /root/docker-images/claude-3.5-sonnet-06c5386831e97e94d9b9fd155d3ea4aa8711c4e7-reproduction.tar claude-3.5-sonnet-06c5386831e97e94d9b9fd155d3ea4aa8711c4e7-reproduction
gzip /root/docker-images/claude-3.5-sonnet-06c5386831e97e94d9b9fd155d3ea4aa8711c4e7-reproduction.tar