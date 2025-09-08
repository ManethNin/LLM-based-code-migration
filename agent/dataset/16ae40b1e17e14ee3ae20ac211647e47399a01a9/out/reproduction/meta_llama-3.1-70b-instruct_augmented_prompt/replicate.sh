#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:16ae40b1e17e14ee3ae20ac211647e47399a01a9-breaking
docker build -t meta-16ae40b1e17e14ee3ae20ac211647e47399a01a9-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/16ae40b1e17e14ee3ae20ac211647e47399a01a9/out/reproduction/meta_llama-3.1-70b-instruct_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:16ae40b1e17e14ee3ae20ac211647e47399a01a9-breaking > pre.txt 2>&1
docker run meta-16ae40b1e17e14ee3ae20ac211647e47399a01a9-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag meta-16ae40b1e17e14ee3ae20ac211647e47399a01a9-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:meta-16ae40b1e17e14ee3ae20ac211647e47399a01a9-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:meta-16ae40b1e17e14ee3ae20ac211647e47399a01a9-reproduction


docker save -o /root/docker-images/meta-16ae40b1e17e14ee3ae20ac211647e47399a01a9-reproduction.tar meta-16ae40b1e17e14ee3ae20ac211647e47399a01a9-reproduction
gzip /root/docker-images/meta-16ae40b1e17e14ee3ae20ac211647e47399a01a9-reproduction.tar