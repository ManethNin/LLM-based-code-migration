#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:bd3ce213e2771c6ef7817c80818807a757d4e94a-breaking
docker build -t claude-3.5-sonnet-bd3ce213e2771c6ef7817c80818807a757d4e94a-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/bd3ce213e2771c6ef7817c80818807a757d4e94a/out/reproduction/claude-3-5-sonnet@20240620_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:bd3ce213e2771c6ef7817c80818807a757d4e94a-breaking > pre.txt 2>&1
docker run claude-3.5-sonnet-bd3ce213e2771c6ef7817c80818807a757d4e94a-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag claude-3.5-sonnet-bd3ce213e2771c6ef7817c80818807a757d4e94a-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-bd3ce213e2771c6ef7817c80818807a757d4e94a-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-bd3ce213e2771c6ef7817c80818807a757d4e94a-reproduction


docker save -o /root/docker-images/claude-3.5-sonnet-bd3ce213e2771c6ef7817c80818807a757d4e94a-reproduction.tar claude-3.5-sonnet-bd3ce213e2771c6ef7817c80818807a757d4e94a-reproduction
gzip /root/docker-images/claude-3.5-sonnet-bd3ce213e2771c6ef7817c80818807a757d4e94a-reproduction.tar