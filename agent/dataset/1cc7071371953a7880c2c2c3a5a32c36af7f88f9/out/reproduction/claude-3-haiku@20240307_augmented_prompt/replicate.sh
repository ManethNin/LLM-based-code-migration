#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:1cc7071371953a7880c2c2c3a5a32c36af7f88f9-breaking
docker build -t claude-3-haiku-1cc7071371953a7880c2c2c3a5a32c36af7f88f9-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/1cc7071371953a7880c2c2c3a5a32c36af7f88f9/out/reproduction/claude-3-haiku@20240307_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:1cc7071371953a7880c2c2c3a5a32c36af7f88f9-breaking > pre.txt 2>&1
docker run claude-3-haiku-1cc7071371953a7880c2c2c3a5a32c36af7f88f9-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag claude-3-haiku-1cc7071371953a7880c2c2c3a5a32c36af7f88f9-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:claude-3-haiku-1cc7071371953a7880c2c2c3a5a32c36af7f88f9-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:claude-3-haiku-1cc7071371953a7880c2c2c3a5a32c36af7f88f9-reproduction


docker save -o /root/docker-images/claude-3-haiku-1cc7071371953a7880c2c2c3a5a32c36af7f88f9-reproduction.tar claude-3-haiku-1cc7071371953a7880c2c2c3a5a32c36af7f88f9-reproduction
gzip /root/docker-images/claude-3-haiku-1cc7071371953a7880c2c2c3a5a32c36af7f88f9-reproduction.tar