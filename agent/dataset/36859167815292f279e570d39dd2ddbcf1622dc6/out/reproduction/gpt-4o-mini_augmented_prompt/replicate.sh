#!/bin/bash

docker pull ghcr.io/chains-project/breaking-updates:36859167815292f279e570d39dd2ddbcf1622dc6-breaking
docker build -t gpt-4o-mini-36859167815292f279e570d39dd2ddbcf1622dc6-reproduction /root/thesis/masterthesis-implementation-gpt/dataset/36859167815292f279e570d39dd2ddbcf1622dc6/out/reproduction/gpt-4o-mini_augmented_prompt
docker run ghcr.io/chains-project/breaking-updates:36859167815292f279e570d39dd2ddbcf1622dc6-breaking > pre.txt 2>&1
docker run gpt-4o-mini-36859167815292f279e570d39dd2ddbcf1622dc6-reproduction > post.txt 2>&1

# Tag and push the reproduction image to GitHub package registry
docker tag gpt-4o-mini-36859167815292f279e570d39dd2ddbcf1622dc6-reproduction ghcr.io/lukvonstrom/masterthesis-implementation:gpt-4o-mini-36859167815292f279e570d39dd2ddbcf1622dc6-reproduction
docker push ghcr.io/lukvonstrom/masterthesis-implementation:gpt-4o-mini-36859167815292f279e570d39dd2ddbcf1622dc6-reproduction


docker save -o /root/docker-images/gpt-4o-mini-36859167815292f279e570d39dd2ddbcf1622dc6-reproduction.tar gpt-4o-mini-36859167815292f279e570d39dd2ddbcf1622dc6-reproduction
gzip /root/docker-images/gpt-4o-mini-36859167815292f279e570d39dd2ddbcf1622dc6-reproduction.tar