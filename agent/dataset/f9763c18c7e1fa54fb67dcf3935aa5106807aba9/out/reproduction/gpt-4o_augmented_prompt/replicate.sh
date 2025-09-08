#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:f9763c18c7e1fa54fb67dcf3935aa5106807aba9-breaking
docker build -t gpt-4o-f9763c18c7e1fa54fb67dcf3935aa5106807aba9-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/f9763c18c7e1fa54fb67dcf3935aa5106807aba9/out/reproduction/gpt-4o_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:f9763c18c7e1fa54fb67dcf3935aa5106807aba9-breaking > pre.txt 2>&1
docker run gpt-4o-f9763c18c7e1fa54fb67dcf3935aa5106807aba9-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag gpt-4o-f9763c18c7e1fa54fb67dcf3935aa5106807aba9-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:gpt-4o-f9763c18c7e1fa54fb67dcf3935aa5106807aba9-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:gpt-4o-f9763c18c7e1fa54fb67dcf3935aa5106807aba9-reproduction


docker save -o /root/docker-images/gpt-4o-f9763c18c7e1fa54fb67dcf3935aa5106807aba9-reproduction.tar gpt-4o-f9763c18c7e1fa54fb67dcf3935aa5106807aba9-reproduction
gzip /root/docker-images/gpt-4o-f9763c18c7e1fa54fb67dcf3935aa5106807aba9-reproduction.tar