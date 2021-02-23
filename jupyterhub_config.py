# Configuration file for JupyterHub
import os
import socket
import dockerspawner
import subprocess
import warnings
from tornado import gen
from oauthenticator.oauth2 import OAuthenticator
from oauthenticator.generic import GenericOAuthenticator
import json
import os
import base64
import urllib

from tornado.auth import OAuth2Mixin
from tornado import web

from tornado.httputil import url_concat
from tornado.httpclient import HTTPRequest, AsyncHTTPClient

from jupyterhub.auth import LocalAuthenticator

from traitlets import Unicode, Dict, Bool, Union, default, observe


c = get_config()

c.JupyterHub.tornado_settings = {'max_body_size': 1048576000, 'max_buffer_size': 1048576000}

callback = os.environ["OAUTH_CALLBACK_URL"]
os.environ["OAUTH_CALLBACK"] = callback
iam_server = os.environ["OAUTH_ENDPOINT"]

server_host = socket.gethostbyname(socket.getfqdn())
os.environ["IAM_INSTANCE"] = iam_server

#c.Spawner.default_url = '/lab'

myenv = os.environ.copy()

cache_file = '/srv/jupyterhub/cookies/iam_secret'

if os.path.isfile(cache_file):
    with open(cache_file) as f:
        cache_results = json.load(f)
else:
    response = subprocess.check_output(['./.init/dodas-IAMClientRec', server_host], env=myenv)
    response_list = response.decode('utf-8').split("\n")
    client_id = response_list[len(response_list)-3]
    client_secret = response_list[len(response_list)-2]

    cache_results = {
        "client_id": client_id,
        "client_secret": client_secret
    }
    with open(cache_file, "w") as w:
        json.dump(cache_results, w)

client_id = cache_results["client_id"]
client_secret = cache_results["client_secret"]


class EnvAuthenticator(GenericOAuthenticator):

    @gen.coroutine
    def pre_spawn_start(self, user, spawner):
        auth_state = yield user.get_auth_state()
        import pprint
        pprint.pprint(auth_state)
        if not auth_state:
            # user has no auth state
            return
        # define some environment variables from auth_state
        self.log.info(auth_state)
        spawner.environment['IAM_SERVER'] = iam_server
        spawner.environment['IAM_CLIENT_ID'] = client_id
        spawner.environment['IAM_CLIENT_SECRET'] = client_secret
        spawner.environment['ACCESS_TOKEN'] = auth_state['access_token']
        spawner.environment['REFRESH_TOKEN'] = auth_state['refresh_token']
        spawner.environment['USERNAME'] = auth_state['oauth_user']['preferred_username']
        spawner.environment['JUPYTERHUB_ACTIVITY_INTERVAL'] = "15"

        amIAllowed = False

        if os.environ.get("OAUTH_GROUPS"):
            spawner.environment['GROUPS'] = " ".join(auth_state['oauth_user']['groups'])
            allowed_groups = os.environ["OAUTH_GROUPS"].split(" ")
            self.log.info(auth_state['oauth_user']['groups'])
            for gr in allowed_groups:
                if gr in auth_state['oauth_user']['groups']:
                    amIAllowed = True
        else:
            amIAllowed = True

        if not amIAllowed:
                self.log.error(
                    "OAuth user contains not in group the allowed groups %s" % allowed_groups
                )
                raise Exception("OAuth user not in the allowed groups %s" % allowed_groups)

c.JupyterHub.authenticator_class = EnvAuthenticator
c.GenericOAuthenticator.oauth_callback_url = callback

c.JupyterHub.db_url = 'sqlite:///db/jupyterhub.sqlite'

# PUT IN SECRET
c.GenericOAuthenticator.client_id = client_id
c.GenericOAuthenticator.client_secret = client_secret
c.GenericOAuthenticator.authorize_url = iam_server.strip('/') + '/authorize'
c.GenericOAuthenticator.token_url = iam_server.strip('/') + '/token'
c.GenericOAuthenticator.userdata_url = iam_server.strip('/') + '/userinfo'
c.GenericOAuthenticator.scope = ['openid', 'profile', 'email', 'address', 'offline_access']
c.GenericOAuthenticator.username_key = "preferred_username"

c.GenericOAuthenticator.enable_auth_state = True
if 'JUPYTERHUB_CRYPT_KEY' not in os.environ:
    warnings.warn(
        "Need JUPYTERHUB_CRYPT_KEY env for persistent auth_state.\n"
        "    export JUPYTERHUB_CRYPT_KEY=$(openssl rand -hex 32)"
    )
    c.CryptKeeper.keys = [ os.urandom(32) ]

c.JupyterHub.log_level = 30

c.JupyterHub.cookie_secret_file = '/srv/jupyterhub/cookies/jupyterhub_cookie_secret'

c.ConfigurableHTTPProxy.debug = True
c.JupyterHub.cleanup_servers = False
c.ConfigurableHTTPProxy.should_start = False
c.ConfigurableHTTPProxy.auth_token = "__ML_TOKEN_HERE__"
c.ConfigurableHTTPProxy.api_url = 'http://http_proxy:8001'


# Spawn single-user servers as Docker containers
class CustomSpawner(dockerspawner.DockerSpawner):
    def _options_form_default(self):
        return """
        <label for="stack">Select your desired image:</label>
  <input list="images" name="img">
  <datalist id="images">
    <option value="dodasts/ml_infn:beta-v2">ML-INFN-DEMO</option>
  </datalist>
<br>
        <label for="mem">Select your desired memory size:</label>
        <select name="mem" size="1">
  <option value="4G">  4GB</option>
  <option value="8G">  8GB </option>
  <option value="16G"> 16GB </option>
  <option value="32G"> 32GB </option>
  <option value="64G"> 64GB </option>
</select>

<br>
        <label for="gpu">GPU:</label>
        <select name="gpu" size="1">
  <option value="Y">Yes</option>
  <option value="N"> No </option>
</select>
"""

    def options_from_form(self, formdata):
        options = {}
        options['img'] = formdata['img']
        container_image = ''.join(formdata['img'])
        print("SPAWN: " + container_image + " IMAGE" )
        self.container_image = container_image
        options['mem'] = formdata['mem']
        memory = ''.join(formdata['mem'])
        self.mem_limit = memory
        options['gpu'] = formdata['gpu']
        use_gpu = True if ''.join(formdata['gpu'])=="Y" else False
        device_request = {}
        if use_gpu:
            device_request = {
                'Driver': 'nvidia',
                'Capabilities': [['gpu']],  # not sure which capabilities are really needed
                'Count': 1,  # enable all gpus
            }
            self.extra_host_config = {
                "cap_add": [
                      "SYS_ADMIN"
                ],
                "privileged": True,
                'device_requests': [device_request]
            }
        else:
            self.extra_host_config = {
                "cap_add": [
                      "SYS_ADMIN"
                ],
                "privileged": True
            }
        return options


    @gen.coroutine
    def create_object(self):
        """Create the container/service object"""

        create_kwargs = dict(
            image=self.image,
            environment=self.get_env(),
            volumes=self.volume_mount_points,
            name=self.container_name,
            command=(yield self.get_command()),
        )

        # ensure internal port is exposed
        create_kwargs["ports"] = {"%i/tcp" % self.port: None}

        create_kwargs.update(self.extra_create_kwargs)

        # build the dictionary of keyword arguments for host_config
        host_config = dict(binds=self.volume_binds, links=self.links)

        if getattr(self, "mem_limit", None) is not None:
            # If jupyterhub version > 0.7, mem_limit is a traitlet that can
            # be directly configured. If so, use it to set mem_limit.
            # this will still be overriden by extra_host_config
            host_config["mem_limit"] = self.mem_limit

        if not self.use_internal_ip:
            host_config["port_bindings"] = {self.port: (self.host_ip,)}
        host_config.update(self.extra_host_config)
        host_config.setdefault("network_mode", self.network_name)

        self.log.debug("Starting host with config: %s", host_config)

        host_config = self.client.create_host_config(**host_config)
        create_kwargs.setdefault("host_config", {}).update(host_config)

        print(create_kwargs)
        # create the container
        obj = yield self.docker("create_container", **create_kwargs)
        return obj

c.JupyterHub.spawner_class = CustomSpawner

# Default spawn to jupyterLab
spawn_cmd = os.environ.get('DOCKER_SPAWN_CMD', "jupyterhub-singleuser --port 8889 --ip 0.0.0.0 --allow-root --debug")
# uncomment to start a jupyter NB instead of jupyterlab
#spawn_cmd = os.environ.get('DOCKER_SPAWN_CMD', "jupyterhub-singleuser --port 8889 --ip 0.0.0.0 --allow-root --debug")

c.DockerSpawner.port = 8889
c.DockerSpawner.extra_create_kwargs.update({ 'command': spawn_cmd })

c.DockerSpawner.network_name = 'jupyterhub'

c.DockerSpawner.http_timeout = 600

# Explicitly set notebook directory because we'll be mounting a host volume to
# it.  Most jupyter/docker-stacks *-notebook images run the Notebook server as
# user `jovyan`, and set the notebook directory to `/home/jovyan/work`.
# We follow the same convention.
#notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR') or '/home/jovyan/work'
#c.DockerSpawner.notebook_dir = notebook_dir

cvmfs_mount_dir = "/cvmfs/"#os.environ.get('DOCKER_NOTEBOOK_DIR') or '/home/jovyan/work'

notebook_mount_dir = "/jupyter-users"#/{username}/"#os.environ.get('DOCKER_NOTEBOOK_DIR') or '/home/jovyan/work'
#notebook_dir = "$PWD/persistent-area/{username}/"#os.environ.get('DOCKER_NOTEBOOK_DIR') or '/home/jovyan/work'
notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR') or '/'
#c.DockerSpawner.notebook_dir = notebook_dir
# Mount the real user's Docker volume on the host to the notebook user's
# notebook directory in the container
#c.DockerSpawner.volumes = { 'jupyterhub-user-{username}': notebook_dir }
c.DockerSpawner.volumes = {  notebook_mount_dir+"/scratch": {"bind": notebook_dir+"/scratch", "mode" : "rw" }, notebook_mount_dir+'/{username}/':
{"bind": notebook_dir+"/persistent_area", "mode" : "rw" }, cvmfs_mount_dir : notebook_dir+"/cvmfs" }

# volume_driver is no longer a keyword argument to create_container()
# c.DockerSpawner.extra_create_kwargs.update({ 'volume_driver': 'local' })
# Remove containers once they are stopped
c.DockerSpawner.remove_containers = True
# For debugging arguments passed to spawned containers
c.DockerSpawner.debug = True

c.JupyterHub.hub_bind_url = 'http://:8088'
c.JupyterHub.hub_connect_ip = 'jupyterhub'

#c.Authenticator.allowed_users = {'test'}
