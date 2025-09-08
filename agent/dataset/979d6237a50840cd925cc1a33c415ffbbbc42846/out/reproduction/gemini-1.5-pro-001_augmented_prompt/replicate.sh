#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:979d6237a50840cd925cc1a33c415ffbbbc42846-breaking
docker build -t gemini-1.5-pro-979d6237a50840cd925cc1a33c415ffbbbc42846-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/979d6237a50840cd925cc1a33c415ffbbbc42846/out/reproduction/gemini-1.5-pro-001_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:979d6237a50840cd925cc1a33c415ffbbbc42846-breaking > pre.txt 2>&1
docker run gemini-1.5-pro-979d6237a50840cd925cc1a33c415ffbbbc42846-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag gemini-1.5-pro-979d6237a50840cd925cc1a33c415ffbbbc42846-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:gemini-1.5-pro-979d6237a50840cd925cc1a33c415ffbbbc42846-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:gemini-1.5-pro-979d6237a50840cd925cc1a33c415ffbbbc42846-reproduction


docker save -o /root/docker-images/gemini-1.5-pro-979d6237a50840cd925cc1a33c415ffbbbc42846-reproduction.tar gemini-1.5-pro-979d6237a50840cd925cc1a33c415ffbbbc42846-reproduction
gzip /root/docker-images/gemini-1.5-pro-979d6237a50840cd925cc1a33c415ffbbbc42846-reproduction.tar