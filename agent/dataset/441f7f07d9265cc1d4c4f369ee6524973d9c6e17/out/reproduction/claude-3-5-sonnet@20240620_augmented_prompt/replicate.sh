#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:441f7f07d9265cc1d4c4f369ee6524973d9c6e17-breaking
docker build -t claude-3.5-sonnet-441f7f07d9265cc1d4c4f369ee6524973d9c6e17-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/441f7f07d9265cc1d4c4f369ee6524973d9c6e17/out/reproduction/claude-3-5-sonnet@20240620_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:441f7f07d9265cc1d4c4f369ee6524973d9c6e17-breaking > pre.txt 2>&1
docker run claude-3.5-sonnet-441f7f07d9265cc1d4c4f369ee6524973d9c6e17-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag claude-3.5-sonnet-441f7f07d9265cc1d4c4f369ee6524973d9c6e17-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-441f7f07d9265cc1d4c4f369ee6524973d9c6e17-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-441f7f07d9265cc1d4c4f369ee6524973d9c6e17-reproduction


docker save -o /root/docker-images/claude-3.5-sonnet-441f7f07d9265cc1d4c4f369ee6524973d9c6e17-reproduction.tar claude-3.5-sonnet-441f7f07d9265cc1d4c4f369ee6524973d9c6e17-reproduction
gzip /root/docker-images/claude-3.5-sonnet-441f7f07d9265cc1d4c4f369ee6524973d9c6e17-reproduction.tar