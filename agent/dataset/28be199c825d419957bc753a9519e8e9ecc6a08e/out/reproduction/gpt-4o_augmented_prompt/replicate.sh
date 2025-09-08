#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:28be199c825d419957bc753a9519e8e9ecc6a08e-breaking
docker build -t gpt-4o-28be199c825d419957bc753a9519e8e9ecc6a08e-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/28be199c825d419957bc753a9519e8e9ecc6a08e/out/reproduction/gpt-4o_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:28be199c825d419957bc753a9519e8e9ecc6a08e-breaking > pre.txt 2>&1
docker run gpt-4o-28be199c825d419957bc753a9519e8e9ecc6a08e-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag gpt-4o-28be199c825d419957bc753a9519e8e9ecc6a08e-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:gpt-4o-28be199c825d419957bc753a9519e8e9ecc6a08e-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:gpt-4o-28be199c825d419957bc753a9519e8e9ecc6a08e-reproduction


docker save -o /root/docker-images/gpt-4o-28be199c825d419957bc753a9519e8e9ecc6a08e-reproduction.tar gpt-4o-28be199c825d419957bc753a9519e8e9ecc6a08e-reproduction
gzip /root/docker-images/gpt-4o-28be199c825d419957bc753a9519e8e9ecc6a08e-reproduction.tar