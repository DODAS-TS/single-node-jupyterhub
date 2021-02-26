FROM tensorflow/tensorflow:latest-gpu-jupyter

ARG JUPYTER_ROOT=/workarea

RUN ln -s /shared ${JUPYTER_ROOT}/shared \
    && ln -s /private ${JUPYTER_ROOT}/private

WORKDIR ${JUPYTER_ROOT}
