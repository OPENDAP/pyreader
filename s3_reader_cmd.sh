#!/bin/bash
#
#

if test -n "$1"
then
    cmd=$1
else
    echo "Usage: s3_reader_cmd <bes cmd file>"
    exit 1
fi

docker exec \
--env CMAC_URL=https://s3-module-test-bucket.s3.us-west-2.amazonaws.com/ \
--env CMAC_REGION=us-west-2 \
--env CMAC_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
--env CMAC_ID=$AWS_ACCESS_KEY_ID \
besd \
besstandalone -c /usr/share/pyreader/pyreader-bes-docker.conf -i /usr/share/pyreader/$cmd
