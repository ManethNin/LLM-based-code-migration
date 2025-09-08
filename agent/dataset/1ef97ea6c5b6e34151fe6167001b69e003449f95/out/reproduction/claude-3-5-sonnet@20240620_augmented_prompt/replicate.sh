#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:1ef97ea6c5b6e34151fe6167001b69e003449f95-breaking
docker build -t claude-3.5-sonnet-1ef97ea6c5b6e34151fe6167001b69e003449f95-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/1ef97ea6c5b6e34151fe6167001b69e003449f95/out/reproduction/claude-3-5-sonnet@20240620_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:1ef97ea6c5b6e34151fe6167001b69e003449f95-breaking > pre.txt 2>&1
docker run claude-3.5-sonnet-1ef97ea6c5b6e34151fe6167001b69e003449f95-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag claude-3.5-sonnet-1ef97ea6c5b6e34151fe6167001b69e003449f95-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-1ef97ea6c5b6e34151fe6167001b69e003449f95-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-1ef97ea6c5b6e34151fe6167001b69e003449f95-reproduction


docker save -o /root/docker-images/claude-3.5-sonnet-1ef97ea6c5b6e34151fe6167001b69e003449f95-reproduction.tar claude-3.5-sonnet-1ef97ea6c5b6e34151fe6167001b69e003449f95-reproduction
gzip /root/docker-images/claude-3.5-sonnet-1ef97ea6c5b6e34151fe6167001b69e003449f95-reproduction.tar