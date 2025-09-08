#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:7e8c62e2bb21097e563747184636cf8e8934ce98-breaking
docker build -t claude-3.5-sonnet-7e8c62e2bb21097e563747184636cf8e8934ce98-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/7e8c62e2bb21097e563747184636cf8e8934ce98/out/reproduction/claude-3-5-sonnet@20240620_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:7e8c62e2bb21097e563747184636cf8e8934ce98-breaking > pre.txt 2>&1
docker run claude-3.5-sonnet-7e8c62e2bb21097e563747184636cf8e8934ce98-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag claude-3.5-sonnet-7e8c62e2bb21097e563747184636cf8e8934ce98-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-7e8c62e2bb21097e563747184636cf8e8934ce98-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-7e8c62e2bb21097e563747184636cf8e8934ce98-reproduction


docker save -o /root/docker-images/claude-3.5-sonnet-7e8c62e2bb21097e563747184636cf8e8934ce98-reproduction.tar claude-3.5-sonnet-7e8c62e2bb21097e563747184636cf8e8934ce98-reproduction
gzip /root/docker-images/claude-3.5-sonnet-7e8c62e2bb21097e563747184636cf8e8934ce98-reproduction.tar