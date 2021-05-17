FROM ubuntu:20.04

EXPOSE 8099

RUN DEBIAN_FRONTEND=noninteractive apt update && apt upgrade -y && apt install -y python3 python3-pip

WORKDIR /usr/share/collab_proxy

RUN pip3 install flask
RUN pip3 install jupyterhub

RUN DEBIAN_FRONTEND=noninteractive apt install -y libcurl4-openssl-dev libssl-dev

COPY collab_proxy.py .

CMD ["python3", "collab_proxy.py"]

