#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:07e4b2894bc68cd3bb1892beaa13ec353564dcf1-breaking
docker build -t claude-3.5-sonnet-07e4b2894bc68cd3bb1892beaa13ec353564dcf1-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/07e4b2894bc68cd3bb1892beaa13ec353564dcf1/out/reproduction/claude-3-5-sonnet@20240620_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:07e4b2894bc68cd3bb1892beaa13ec353564dcf1-breaking > pre.txt 2>&1
docker run claude-3.5-sonnet-07e4b2894bc68cd3bb1892beaa13ec353564dcf1-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag claude-3.5-sonnet-07e4b2894bc68cd3bb1892beaa13ec353564dcf1-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-07e4b2894bc68cd3bb1892beaa13ec353564dcf1-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-07e4b2894bc68cd3bb1892beaa13ec353564dcf1-reproduction


docker save -o /root/docker-images/claude-3.5-sonnet-07e4b2894bc68cd3bb1892beaa13ec353564dcf1-reproduction.tar claude-3.5-sonnet-07e4b2894bc68cd3bb1892beaa13ec353564dcf1-reproduction
gzip /root/docker-images/claude-3.5-sonnet-07e4b2894bc68cd3bb1892beaa13ec353564dcf1-reproduction.tar