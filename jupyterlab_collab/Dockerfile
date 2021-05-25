FROM ubuntu:20.04

EXPOSE 8000
EXPOSE 8888

RUN DEBIAN_FRONTEND=noninteractive apt update && apt upgrade -y && apt install -y git

WORKDIR /usr/share

RUN git clone https://github.com/jupyter-rtc/jupyterlab.git

WORKDIR /

RUN DEBIAN_FRONTEND=noninteractive apt install -y build-essential python3-dev python3-pip libargon2-0-dev \
    libffi-dev libpixman-1-dev libcairo2-dev libpangox-1.0-dev libjpeg-dev \
    libczmq-dev

RUN python3 -m pip install -U pip setuptools
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y curl

WORKDIR /usr/share/jupyterlab

COPY force_collab.patch .

RUN git apply force_collab.patch
RUN python3 -m pip install --no-cache-dir idna==2.10
RUN python3 -m pip install --no-cache-dir importlib-metadata==3.10.1
RUN python3 setup.py install
RUN python3 -m pip install --no-cache-dir jupyterlab-link-share

RUN curl -fsSL https://deb.nodesource.com/setup_14.x | bash -
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y nodejs
RUN jlpm
RUN npm run-script "build:dev:prod:release"
RUN /bin/bash -c "mkdir -p /usr/local/share/jupyter/lab/"
RUN /bin/bash -c "jupyter lab build"
RUN /bin/bash -c "cp -r /usr/share/jupyterlab/dev_mode/{static,schemas,themes} /usr/local/share/jupyter/lab/"

RUN DEBIAN_FRONTEND=noninteractive apt install -y libcurl4-openssl-dev libssl-dev
RUN python3 -m pip install --no-cache-dir jupyterhub pycurl
RUN npm install -g configurable-http-proxy
RUN jupyter serverextension enable --py jupyterlab --sys-prefix

COPY jupyterhub_config.py /etc/jupyterhub/

WORKDIR /usr/share/workspace

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--debug", \
    "--ServerApp.allow_password_change=False", \
    "--ServerApp.keyfile=/usr/local/share/certs/jupyter/hostcert.key", \
    "--ServerApp.certfile=/usr/local/share/certs/jupyter/hostcert.pem", \
    "--MappingKernelManager.cull_idle_timeout=10800", \
    "--MappingKernelManager.cull_connected=True"]
