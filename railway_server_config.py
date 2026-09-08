import os

c = get_config()

token = os.environ.get("JUPYTER_TOKEN", "")
if not token.strip():
    raise ValueError("JUPYTER_TOKEN must not be empty")
port = int(os.environ.get("PORT", "8888"))
if not 1 <= port <= 65535:
    raise ValueError("PORT must be between 1 and 65535")

c.IdentityProvider.token = token
c.PasswordIdentityProvider.allow_password_change = False
c.ServerApp.ip = "0.0.0.0"
c.ServerApp.port = port
c.ServerApp.port_retries = 0
c.ServerApp.open_browser = False
c.ServerApp.root_dir = "/home/jovyan"
c.ServerApp.trust_xheaders = True
# Railway's healthcheck uses a hostname other than the public domain.
c.ServerApp.allow_remote_access = True
c.ServerApp.log_level = "WARN"
c.FileContentsManager.delete_to_trash = False
