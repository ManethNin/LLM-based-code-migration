#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:26fd1cd7639b7deb7078df5e4cb05c6d463ad07a-breaking
docker build -t gpt-4o-26fd1cd7639b7deb7078df5e4cb05c6d463ad07a-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/26fd1cd7639b7deb7078df5e4cb05c6d463ad07a/out/reproduction/gpt-4o_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:26fd1cd7639b7deb7078df5e4cb05c6d463ad07a-breaking > pre.txt 2>&1
docker run gpt-4o-26fd1cd7639b7deb7078df5e4cb05c6d463ad07a-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag gpt-4o-26fd1cd7639b7deb7078df5e4cb05c6d463ad07a-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:gpt-4o-26fd1cd7639b7deb7078df5e4cb05c6d463ad07a-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:gpt-4o-26fd1cd7639b7deb7078df5e4cb05c6d463ad07a-reproduction


docker save -o /root/docker-images/gpt-4o-26fd1cd7639b7deb7078df5e4cb05c6d463ad07a-reproduction.tar gpt-4o-26fd1cd7639b7deb7078df5e4cb05c6d463ad07a-reproduction
gzip /root/docker-images/gpt-4o-26fd1cd7639b7deb7078df5e4cb05c6d463ad07a-reproduction.tar