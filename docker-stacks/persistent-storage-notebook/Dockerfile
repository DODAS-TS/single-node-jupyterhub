FROM ubuntu:18.04

ARG JUPYTER_ROOT=/workarea

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \ 
    wget \
    fuse \
    git \
    software-properties-common \
    ca-certificates

RUN wget "https://crt.sh/?d=2475254782" -O /usr/local/share/ca-certificates/ca.crt && \                                      
    update-ca-certificates 

RUN python3 -m pip --no-cache-dir install --upgrade pip

RUN pip install --no-cache-dir jupyterhub notebook \
    && pip3 install -U git+https://github.com/DODAS-TS/boto3sts

# Automount S3 with sts-wire
COPY custom-spawner/jupyterhub-singleuser /usr/local/bin/jupyterhub-singleuser
COPY custom-spawner/spawn.sh ./.init/spawn.sh
COPY examples ${JUPYTER_ROOT}/examples

RUN chmod +x /usr/local/bin/jupyterhub-singleuser \
    && chmod +x ./.init/spawn.sh

RUN apt-key adv --keyserver hkp://pgp.surfnet.nl --recv-keys ACDFB08FDC962044D87FF00B512839863D487A87 \
    && add-apt-repository "deb http://repo.data.kit.edu/ubuntu/bionic ./" \
    && apt-get update \
    && apt-get install -y oidc-agent

RUN mkdir -p .init \
    && wget https://github.com/DODAS-TS/sts-wire/releases/download/v1.2.2/sts-wire_linux -O ./.init/sts-wire \
    && chmod +x ./.init/sts-wire

#RUN mkdir ${JUPYTER_ROOT}
RUN ln -s /s3 ${JUPYTER_ROOT}/cloud-storage \
    && ln -s /shared ${JUPYTER_ROOT}/shared \
    && ln -s /private ${JUPYTER_ROOT}/private

WORKDIR ${JUPYTER_ROOT}
