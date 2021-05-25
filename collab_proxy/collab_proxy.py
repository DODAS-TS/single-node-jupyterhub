from functools import wraps
import json
import os
from urllib.parse import quote

from flask import Flask, redirect, request, Response

from jupyterhub.services.auth import HubAuth

prefix = os.environ.get("JUPYTERHUB_SERVICE_PREFIX", "/")
jupyter_token = os.environ.get("JUPYTER_TOKEN", "")
host_ip = os.environ.get("HOST_IP", "0.0.0.0")

auth = HubAuth(
    api_token=os.environ["JUPYTERHUB_API_TOKEN"],
    cache_max_age=60,
)

app = Flask(__name__)


def authenticated(f):
    """Decorator for authenticating with the Hub"""

    @wraps(f)
    def decorated(*args, **kwargs):
        cookie = request.cookies.get(auth.cookie_name)
        token = request.headers.get(auth.auth_header_name)
        if cookie:
            user = auth.user_for_cookie(cookie)
        elif token:
            user = auth.user_for_token(token)
        else:
            user = None
        if user:
            return f(user, *args, **kwargs)
        else:
            # redirect to login url on failed auth
            # return redirect(auth.login_url + '?next=%s' % quote(request.path))
            return redirect(f"https://{host_ip}:8888/login?")

    return decorated


@app.route(prefix)
@authenticated
def go_to_jupyterlab_collab(user):
    return redirect(f"https://{host_ip}:8889/lab?token={jupyter_token}")
    # return Response(
    #     json.dumps(user, indent=1, sort_keys=True),
    #     mimetype='application/json',
    #     )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8099)
