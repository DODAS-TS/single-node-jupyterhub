FROM ubuntu:18.04

ARG JUPYTER_ROOT=/workarea

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip

RUN python3 -m pip --no-cache-dir install --upgrade pip

RUN pip install --no-cache-dir jupyterhub notebook

# Automount S3 with sts-wire
COPY custom-spawner/jupyterhub-singleuser /usr/local/bin/jupyterhub-singleuser
COPY custom-spawner/spawn.sh ./.init/spawn.sh

RUN chmod +x /usr/local/bin/jupyterhub-singleuser \
    && chmod +x ./.init/spawn.sh

RUN apt-get install -y software-properties-common \
    fuse

RUN apt-key adv --keyserver hkp://pgp.surfnet.nl --recv-keys ACDFB08FDC962044D87FF00B512839863D487A87 \
    && add-apt-repository "deb http://repo.data.kit.edu/ubuntu/bionic ./" \
    && apt-get update \
    && apt-get install -y oidc-agent

RUN mkdir -p .init \
    && wget https://github.com/DODAS-TS/sts-wire/releases/download/v1.1.0/sts-wire_linux -O ./.init/sts-wire \
    && chmod +x ./.init/sts-wire

RUN mkdir ${JUPYTER_ROOT}
RUN ln -s /s3 ${JUPYTER_ROOT}/cloud-storage \
    && ln -s /shared ${JUPYTER_ROOT}/shared \
    && ln -s /private ${JUPYTER_ROOT}/private

WORKDIR ${JUPYTER_ROOT}
