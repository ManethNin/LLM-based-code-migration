#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:c09896887acf0fe59320e01145a7034cd8d4e326-breaking
docker build -t claude-3.5-sonnet-c09896887acf0fe59320e01145a7034cd8d4e326-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/c09896887acf0fe59320e01145a7034cd8d4e326/out/reproduction/claude-3-5-sonnet@20240620_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:c09896887acf0fe59320e01145a7034cd8d4e326-breaking > pre.txt 2>&1
docker run claude-3.5-sonnet-c09896887acf0fe59320e01145a7034cd8d4e326-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag claude-3.5-sonnet-c09896887acf0fe59320e01145a7034cd8d4e326-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-c09896887acf0fe59320e01145a7034cd8d4e326-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-c09896887acf0fe59320e01145a7034cd8d4e326-reproduction


docker save -o /root/docker-images/claude-3.5-sonnet-c09896887acf0fe59320e01145a7034cd8d4e326-reproduction.tar claude-3.5-sonnet-c09896887acf0fe59320e01145a7034cd8d4e326-reproduction
gzip /root/docker-images/claude-3.5-sonnet-c09896887acf0fe59320e01145a7034cd8d4e326-reproduction.tar