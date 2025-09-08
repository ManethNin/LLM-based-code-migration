#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:18eff0121ded81b30af0924676407bfc663e6557-breaking
docker build -t claude-3.5-sonnet-18eff0121ded81b30af0924676407bfc663e6557-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/18eff0121ded81b30af0924676407bfc663e6557/out/reproduction/claude-3-5-sonnet@20240620_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:18eff0121ded81b30af0924676407bfc663e6557-breaking > pre.txt 2>&1
docker run claude-3.5-sonnet-18eff0121ded81b30af0924676407bfc663e6557-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag claude-3.5-sonnet-18eff0121ded81b30af0924676407bfc663e6557-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-18eff0121ded81b30af0924676407bfc663e6557-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-18eff0121ded81b30af0924676407bfc663e6557-reproduction


docker save -o /root/docker-images/claude-3.5-sonnet-18eff0121ded81b30af0924676407bfc663e6557-reproduction.tar claude-3.5-sonnet-18eff0121ded81b30af0924676407bfc663e6557-reproduction
gzip /root/docker-images/claude-3.5-sonnet-18eff0121ded81b30af0924676407bfc663e6557-reproduction.tar