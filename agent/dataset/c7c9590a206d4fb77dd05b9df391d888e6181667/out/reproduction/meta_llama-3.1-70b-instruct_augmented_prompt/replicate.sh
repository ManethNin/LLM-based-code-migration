#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:c7c9590a206d4fb77dd05b9df391d888e6181667-breaking
docker build -t meta-c7c9590a206d4fb77dd05b9df391d888e6181667-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/c7c9590a206d4fb77dd05b9df391d888e6181667/out/reproduction/meta_llama-3.1-70b-instruct_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:c7c9590a206d4fb77dd05b9df391d888e6181667-breaking > pre.txt 2>&1
docker run meta-c7c9590a206d4fb77dd05b9df391d888e6181667-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag meta-c7c9590a206d4fb77dd05b9df391d888e6181667-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:meta-c7c9590a206d4fb77dd05b9df391d888e6181667-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:meta-c7c9590a206d4fb77dd05b9df391d888e6181667-reproduction


docker save -o /root/docker-images/meta-c7c9590a206d4fb77dd05b9df391d888e6181667-reproduction.tar meta-c7c9590a206d4fb77dd05b9df391d888e6181667-reproduction
gzip /root/docker-images/meta-c7c9590a206d4fb77dd05b9df391d888e6181667-reproduction.tar