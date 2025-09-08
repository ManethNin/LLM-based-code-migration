#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:88c1f903cede03ff371059cdaf009dab12007043-breaking
docker build -t claude-3-haiku-88c1f903cede03ff371059cdaf009dab12007043-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/88c1f903cede03ff371059cdaf009dab12007043/out/reproduction/claude-3-haiku@20240307_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:88c1f903cede03ff371059cdaf009dab12007043-breaking > pre.txt 2>&1
docker run claude-3-haiku-88c1f903cede03ff371059cdaf009dab12007043-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag claude-3-haiku-88c1f903cede03ff371059cdaf009dab12007043-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:claude-3-haiku-88c1f903cede03ff371059cdaf009dab12007043-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:claude-3-haiku-88c1f903cede03ff371059cdaf009dab12007043-reproduction


docker save -o /root/docker-images/claude-3-haiku-88c1f903cede03ff371059cdaf009dab12007043-reproduction.tar claude-3-haiku-88c1f903cede03ff371059cdaf009dab12007043-reproduction
gzip /root/docker-images/claude-3-haiku-88c1f903cede03ff371059cdaf009dab12007043-reproduction.tar