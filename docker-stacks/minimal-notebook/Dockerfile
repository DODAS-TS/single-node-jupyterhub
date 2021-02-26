FROM ubuntu:18.04

ARG JUPYTER_ROOT=/workarea

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip

RUN python3 -m pip --no-cache-dir install --upgrade pip

RUN pip install --no-cache-dir jupyterhub notebook

RUN ln -s /shared ${JUPYTER_ROOT}/shared \
    && ln -s /private ${JUPYTER_ROOT}/private

WORKDIR ${JUPYTER_ROOT}

