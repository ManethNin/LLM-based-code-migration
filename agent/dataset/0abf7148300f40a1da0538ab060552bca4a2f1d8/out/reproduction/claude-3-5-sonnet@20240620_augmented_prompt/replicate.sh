#!/bin/bash

    docker pull ghcr.io/chains-project/breaking-updates:0abf7148300f40a1da0538ab060552bca4a2f1d8-breaking
    docker build -t claude-3.5-sonnet-0abf7148300f40a1da0538ab060552bca4a2f1d8-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/0abf7148300f40a1da0538ab060552bca4a2f1d8/out/reproduction/claude-3-5-sonnet@20240620_augmented_prompt
    docker run ghcr.io/chains-project/breaking-updates:0abf7148300f40a1da0538ab060552bca4a2f1d8-breaking > pre.txt 2>&1
    docker run claude-3.5-sonnet-0abf7148300f40a1da0538ab060552bca4a2f1d8-reproduction > post.txt 2>&1

    # Tag and push the reproduction image to GitHub package registry
    docker tag claude-3.5-sonnet-0abf7148300f40a1da0538ab060552bca4a2f1d8-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-0abf7148300f40a1da0538ab060552bca4a2f1d8-reproduction
    docker push ghcr.io/lukvonstrom/masterthesis-implementation:claude-3.5-sonnet-0abf7148300f40a1da0538ab060552bca4a2f1d8-reproduction
    