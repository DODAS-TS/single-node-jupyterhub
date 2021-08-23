#!/bin/bash

kill `ps faux | grep "sts-wire ${USERNAME}" | awk '{ print $2 }'`
kill `ps faux | grep ".${USERNAME}" | awk '{ print $2 }'`
kill `ps faux | grep "sts-wire scratch" | awk '{ print $2 }'`
kill `ps faux | grep ".scratch" | awk '{ print $2 }'`

mkdir -p /s3/
mkdir -p /s3/${USERNAME}
mkdir -p /s3/scratch

cd /.init/


./sts-wire https://iam.cloud.infn.it/  ${USERNAME} https://minio.cloud.infn.it/ /${USERNAME} ../s3/${USERNAME} > .mount_log_${USERNAME}.txt &
./sts-wire https://iam.cloud.infn.it/ scratch https://minio.cloud.infn.it/  /scratch ../s3/scratch > .mount_log_scratch.txt &
