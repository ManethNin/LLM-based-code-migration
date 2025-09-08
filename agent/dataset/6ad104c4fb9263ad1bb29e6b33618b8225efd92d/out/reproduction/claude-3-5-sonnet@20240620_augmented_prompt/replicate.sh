#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:6ad104c4fb9263ad1bb29e6b33618b8225efd92d-breaking
docker build -t claude-3.5-sonnet-6ad104c4fb9263ad1bb29e6b33618b8225efd92d-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/6ad104c4fb9263ad1bb29e6b33618b8225efd92d/out/reproduction/claude-3-5-sonnet@20240620_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:6ad104c4fb9263ad1bb29e6b33618b8225efd92d-breaking > pre.txt 2>&1
docker run claude-3.5-sonnet-6ad104c4fb9263ad1bb29e6b33618b8225efd92d-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag claude-3.5-sonnet-6ad104c4fb9263ad1bb29e6b33618b8225efd92d-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-6ad104c4fb9263ad1bb29e6b33618b8225efd92d-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-6ad104c4fb9263ad1bb29e6b33618b8225efd92d-reproduction


docker save -o /root/docker-images/claude-3.5-sonnet-6ad104c4fb9263ad1bb29e6b33618b8225efd92d-reproduction.tar claude-3.5-sonnet-6ad104c4fb9263ad1bb29e6b33618b8225efd92d-reproduction
gzip /root/docker-images/claude-3.5-sonnet-6ad104c4fb9263ad1bb29e6b33618b8225efd92d-reproduction.tar