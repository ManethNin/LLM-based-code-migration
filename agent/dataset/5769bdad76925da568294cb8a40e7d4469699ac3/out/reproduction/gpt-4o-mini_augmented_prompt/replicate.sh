#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:5769bdad76925da568294cb8a40e7d4469699ac3-breaking
docker build -t gpt-4o-mini-5769bdad76925da568294cb8a40e7d4469699ac3-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/5769bdad76925da568294cb8a40e7d4469699ac3/out/reproduction/gpt-4o-mini_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:5769bdad76925da568294cb8a40e7d4469699ac3-breaking > pre.txt 2>&1
docker run gpt-4o-mini-5769bdad76925da568294cb8a40e7d4469699ac3-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag gpt-4o-mini-5769bdad76925da568294cb8a40e7d4469699ac3-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:gpt-4o-mini-5769bdad76925da568294cb8a40e7d4469699ac3-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:gpt-4o-mini-5769bdad76925da568294cb8a40e7d4469699ac3-reproduction


docker save -o /root/docker-images/gpt-4o-mini-5769bdad76925da568294cb8a40e7d4469699ac3-reproduction.tar gpt-4o-mini-5769bdad76925da568294cb8a40e7d4469699ac3-reproduction
gzip /root/docker-images/gpt-4o-mini-5769bdad76925da568294cb8a40e7d4469699ac3-reproduction.tar