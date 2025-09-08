#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:8ab7a7214f9ac1d130b416fae7280cfda533a54f-breaking
docker build -t claude-3.5-sonnet-8ab7a7214f9ac1d130b416fae7280cfda533a54f-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/8ab7a7214f9ac1d130b416fae7280cfda533a54f/out/reproduction/claude-3-5-sonnet@20240620_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:8ab7a7214f9ac1d130b416fae7280cfda533a54f-breaking > pre.txt 2>&1
docker run claude-3.5-sonnet-8ab7a7214f9ac1d130b416fae7280cfda533a54f-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag claude-3.5-sonnet-8ab7a7214f9ac1d130b416fae7280cfda533a54f-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-8ab7a7214f9ac1d130b416fae7280cfda533a54f-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-8ab7a7214f9ac1d130b416fae7280cfda533a54f-reproduction


docker save -o /root/docker-images/claude-3.5-sonnet-8ab7a7214f9ac1d130b416fae7280cfda533a54f-reproduction.tar claude-3.5-sonnet-8ab7a7214f9ac1d130b416fae7280cfda533a54f-reproduction
gzip /root/docker-images/claude-3.5-sonnet-8ab7a7214f9ac1d130b416fae7280cfda533a54f-reproduction.tar