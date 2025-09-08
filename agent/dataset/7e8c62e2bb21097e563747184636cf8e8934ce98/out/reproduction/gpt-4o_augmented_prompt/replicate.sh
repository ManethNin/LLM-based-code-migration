#!/bin/bash

    docker pull ghcr.io/chains-project/breaking-updates:7e8c62e2bb21097e563747184636cf8e8934ce98-breaking
    docker build -t gpt-4o-7e8c62e2bb21097e563747184636cf8e8934ce98-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/7e8c62e2bb21097e563747184636cf8e8934ce98/out/reproduction/gpt-4o_augmented_prompt
    docker run ghcr.io/chains-project/breaking-updates:7e8c62e2bb21097e563747184636cf8e8934ce98-breaking > pre.txt 2>&1
    docker run gpt-4o-7e8c62e2bb21097e563747184636cf8e8934ce98-reproduction > post.txt 2>&1

    # Tag and push the reproduction image to GitHub package registry
    docker tag gpt-4o-7e8c62e2bb21097e563747184636cf8e8934ce98-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:gpt-4o-7e8c62e2bb21097e563747184636cf8e8934ce98-reproduction
    docker push ghcr.io/lukvonstrom/masterthesis-implementation:gpt-4o-7e8c62e2bb21097e563747184636cf8e8934ce98-reproduction
    