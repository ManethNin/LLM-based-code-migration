#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:54857351e0b0a655970d7e2ccdb67f175cc5d688-breaking
docker build -t meta-54857351e0b0a655970d7e2ccdb67f175cc5d688-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/54857351e0b0a655970d7e2ccdb67f175cc5d688/out/reproduction/meta_llama-3.1-70b-instruct_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:54857351e0b0a655970d7e2ccdb67f175cc5d688-breaking > pre.txt 2>&1
docker run meta-54857351e0b0a655970d7e2ccdb67f175cc5d688-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag meta-54857351e0b0a655970d7e2ccdb67f175cc5d688-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:meta-54857351e0b0a655970d7e2ccdb67f175cc5d688-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:meta-54857351e0b0a655970d7e2ccdb67f175cc5d688-reproduction


docker save -o /root/docker-images/meta-54857351e0b0a655970d7e2ccdb67f175cc5d688-reproduction.tar meta-54857351e0b0a655970d7e2ccdb67f175cc5d688-reproduction
gzip /root/docker-images/meta-54857351e0b0a655970d7e2ccdb67f175cc5d688-reproduction.tar