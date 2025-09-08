#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:6c53cd904bd66fc79af8687571e607c259226b81-breaking
docker build -t gemini-1.5-pro-6c53cd904bd66fc79af8687571e607c259226b81-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/6c53cd904bd66fc79af8687571e607c259226b81/out/reproduction/gemini-1.5-pro-001_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:6c53cd904bd66fc79af8687571e607c259226b81-breaking > pre.txt 2>&1
docker run gemini-1.5-pro-6c53cd904bd66fc79af8687571e607c259226b81-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag gemini-1.5-pro-6c53cd904bd66fc79af8687571e607c259226b81-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:gemini-1.5-pro-6c53cd904bd66fc79af8687571e607c259226b81-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:gemini-1.5-pro-6c53cd904bd66fc79af8687571e607c259226b81-reproduction


docker save -o /root/docker-images/gemini-1.5-pro-6c53cd904bd66fc79af8687571e607c259226b81-reproduction.tar gemini-1.5-pro-6c53cd904bd66fc79af8687571e607c259226b81-reproduction
gzip /root/docker-images/gemini-1.5-pro-6c53cd904bd66fc79af8687571e607c259226b81-reproduction.tar