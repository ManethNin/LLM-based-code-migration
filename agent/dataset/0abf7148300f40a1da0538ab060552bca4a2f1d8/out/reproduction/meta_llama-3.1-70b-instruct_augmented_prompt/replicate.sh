#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:0abf7148300f40a1da0538ab060552bca4a2f1d8-breaking
docker build -t meta-0abf7148300f40a1da0538ab060552bca4a2f1d8-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/0abf7148300f40a1da0538ab060552bca4a2f1d8/out/reproduction/meta_llama-3.1-70b-instruct_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:0abf7148300f40a1da0538ab060552bca4a2f1d8-breaking > pre.txt 2>&1
docker run meta-0abf7148300f40a1da0538ab060552bca4a2f1d8-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag meta-0abf7148300f40a1da0538ab060552bca4a2f1d8-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:meta-0abf7148300f40a1da0538ab060552bca4a2f1d8-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:meta-0abf7148300f40a1da0538ab060552bca4a2f1d8-reproduction


docker save -o /root/docker-images/meta-0abf7148300f40a1da0538ab060552bca4a2f1d8-reproduction.tar meta-0abf7148300f40a1da0538ab060552bca4a2f1d8-reproduction
gzip /root/docker-images/meta-0abf7148300f40a1da0538ab060552bca4a2f1d8-reproduction.tar