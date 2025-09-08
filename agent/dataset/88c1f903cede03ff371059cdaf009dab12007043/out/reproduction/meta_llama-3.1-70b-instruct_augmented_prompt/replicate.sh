#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:88c1f903cede03ff371059cdaf009dab12007043-breaking
docker build -t meta-88c1f903cede03ff371059cdaf009dab12007043-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/88c1f903cede03ff371059cdaf009dab12007043/out/reproduction/meta_llama-3.1-70b-instruct_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:88c1f903cede03ff371059cdaf009dab12007043-breaking > pre.txt 2>&1
docker run meta-88c1f903cede03ff371059cdaf009dab12007043-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag meta-88c1f903cede03ff371059cdaf009dab12007043-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:meta-88c1f903cede03ff371059cdaf009dab12007043-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:meta-88c1f903cede03ff371059cdaf009dab12007043-reproduction


docker save -o /root/docker-images/meta-88c1f903cede03ff371059cdaf009dab12007043-reproduction.tar meta-88c1f903cede03ff371059cdaf009dab12007043-reproduction
gzip /root/docker-images/meta-88c1f903cede03ff371059cdaf009dab12007043-reproduction.tar