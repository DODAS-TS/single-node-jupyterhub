# Single node jupyterhub

## Configure the host machine

The following instructions are valid for an Ubuntu OS.

### Install NVIDIA driver

T4 GPU is taken as an example:

```bash
apt update
apt upgrade -y
apt install -y gcc make
wget https://us.download.nvidia.com/tesla/450.80.02/NVIDIA-Linux-x86_64-450.80.02.run
chmod +x NVIDIA-Linux-x86_64-450.80.02.run
```

Now you are ready to proceed with the interactive installation:

```bash
./NVIDIA-Linux-x86_64-450.80.02.run
```

### Install Docker

```bash
sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common

 curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io
```

Include also docker-compose:

```bash
sudo curl -L "https://github.com/docker/compose/releases/download/1.27.4/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
```

### Install NVIDIA-Docker


``` bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)    && curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -    && curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
apt-get update
sudo apt-get install -y nvidia-docker2
systemctl restart docker
```

## Test your GPU setup

Check that all your GPUs are visible with:

```bash
docker run --rm --gpus all nvidia/cuda nvidia-smi
```

## Bringup JupyterHUB with OAuth authentication

Download this repo:

```bash
git clone https://github.com/dodas-ts/single-node-jupyterhub
cd single-node-jupyterhub
```

Compile the docker-compose.yaml file with your preferences:

```yaml
version: '3.7'
services:
  jupyterhub:
    build: .
    command:
      - /opt/conda/bin/python
      - /opt/conda/bin/jupyterhub
      - --debug
    volumes:
    - /var/run/docker.sock:/var/run/docker.sock
    ports:
    - 8888:8888
    environment:
    - OAUTH_ENDPOINT=https://iam.cloud.infn.it
    - OAUTH_CALLBACK_URL=http://<HERE pub ip of the server>:8888/hub/oauth_callback
    - OAUTH_GROUPS=group1 group2
    - WITH_GPU=true

networks:
  default:
    name: jupyterhub
```

Bring up your hub server with:

```bash
docker-compose up -d
```

### Reach out for the hub

You should be able to login at `http://<yourIP>:8888/hub`


