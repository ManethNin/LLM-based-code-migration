#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:500d9c021d34b307b1a70d3f29fb7f9b5ab9d1a6-breaking
docker build -t claude-3.5-sonnet-500d9c021d34b307b1a70d3f29fb7f9b5ab9d1a6-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/500d9c021d34b307b1a70d3f29fb7f9b5ab9d1a6/out/reproduction/claude-3-5-sonnet@20240620_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:500d9c021d34b307b1a70d3f29fb7f9b5ab9d1a6-breaking > pre.txt 2>&1
docker run claude-3.5-sonnet-500d9c021d34b307b1a70d3f29fb7f9b5ab9d1a6-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag claude-3.5-sonnet-500d9c021d34b307b1a70d3f29fb7f9b5ab9d1a6-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-500d9c021d34b307b1a70d3f29fb7f9b5ab9d1a6-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-500d9c021d34b307b1a70d3f29fb7f9b5ab9d1a6-reproduction


docker save -o /root/docker-images/claude-3.5-sonnet-500d9c021d34b307b1a70d3f29fb7f9b5ab9d1a6-reproduction.tar claude-3.5-sonnet-500d9c021d34b307b1a70d3f29fb7f9b5ab9d1a6-reproduction
gzip /root/docker-images/claude-3.5-sonnet-500d9c021d34b307b1a70d3f29fb7f9b5ab9d1a6-reproduction.tar