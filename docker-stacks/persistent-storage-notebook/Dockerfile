FROM ubuntu:18.04 AS PRE

RUN apt-get update && apt-get install -y \
    software-properties-common \
    help2man \
    check \
    devscripts \
    make \
    sudo \
    ca-certificates \
    libcurl4-openssl-dev \
    libsodium-dev \
    libseccomp-dev \
    libmicrohttpd-dev \
    libsecret-1-dev \
    python3 \
    python3-pip \ 
    wget \
    fuse \
    git 

FROM PRE AS COMPILE

ARG JUPYTER_ROOT=/workarea

RUN apt-get update && apt-get install -y \
    build-essential \
    debhelper \
    pkg-config \
    perl \
    sed \
    fakeroot

RUN cd /opt/ && git clone https://github.com/indigo-dc/oidc-agent \
    && cd oidc-agent \
    && make

FROM PRE as BASE

COPY --from=COMPILE /opt/oidc-agent /opt/oidc-agent

RUN cd /opt/oidc-agent && make install_lib \
    && make install

ARG JUPYTER_ROOT=/workarea


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

RUN mkdir -p .init \
    && wget https://github.com/DODAS-TS/sts-wire/releases/download/v2.0.0/sts-wire_linux -O ./.init/sts-wire \
    && chmod +x ./.init/sts-wire

#RUN mkdir ${JUPYTER_ROOT}
RUN ln -s /s3 ${JUPYTER_ROOT}/cloud-storage \
    && ln -s /shared ${JUPYTER_ROOT}/shared \
    && ln -s /private ${JUPYTER_ROOT}/private

WORKDIR ${JUPYTER_ROOT}
