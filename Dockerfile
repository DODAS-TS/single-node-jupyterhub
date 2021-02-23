FROM dciangot/dodas-iam-client-rec:test5 as REGISTRATION

FROM jupyterhub/jupyterhub:0.9.4
COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --no-cache -r /tmp/requirements.txt
RUN useradd test -p "$(openssl passwd -1 test)"
RUN mkdir /home/test && chown test: /home/test
COPY jupyterhub_config.py /srv/jupyterhub/jupyterhub_config.py

RUN mkdir -p .init

# COPY self registration da docker
COPY --from=REGISTRATION /usr/local/bin/dodas-IAMClientRec ./.init/dodas-IAMClientRec
