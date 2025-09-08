#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:b8f92ff37d1aed054d8320283fd6d6a492703a55-breaking
docker build -t claude-3.5-sonnet-b8f92ff37d1aed054d8320283fd6d6a492703a55-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/b8f92ff37d1aed054d8320283fd6d6a492703a55/out/reproduction/claude-3-5-sonnet@20240620_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:b8f92ff37d1aed054d8320283fd6d6a492703a55-breaking > pre.txt 2>&1
docker run claude-3.5-sonnet-b8f92ff37d1aed054d8320283fd6d6a492703a55-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag claude-3.5-sonnet-b8f92ff37d1aed054d8320283fd6d6a492703a55-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-b8f92ff37d1aed054d8320283fd6d6a492703a55-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-b8f92ff37d1aed054d8320283fd6d6a492703a55-reproduction


docker save -o /root/docker-images/claude-3.5-sonnet-b8f92ff37d1aed054d8320283fd6d6a492703a55-reproduction.tar claude-3.5-sonnet-b8f92ff37d1aed054d8320283fd6d6a492703a55-reproduction
gzip /root/docker-images/claude-3.5-sonnet-b8f92ff37d1aed054d8320283fd6d6a492703a55-reproduction.tar