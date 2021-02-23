#!/bin/bash
cd /tf/
kill `ps faux | grep "sts-wire ${USERNAME}" | awk '{ print $2 }'`
kill `ps faux | grep ".${USERNAME}" | awk '{ print $2 }'`
kill `ps faux | grep "sts-wire scratch" | awk '{ print $2 }'`
kill `ps faux | grep ".scratch" | awk '{ print $2 }'`
mkdir -p s3/${USERNAME}
mkdir -p s3/scratch
cd .init/
./sts-wire ${USERNAME} https://131.154.97.112:9000/ /${USERNAME} ../s3/${USERNAME} > .mount_log_${USERNAME}.txt &
./sts-wire scratch https://131.154.97.112:9000/ /scratch ../s3/scratch > .mount_log_scratch.txt &

