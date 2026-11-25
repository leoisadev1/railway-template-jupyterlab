FROM quay.io/jupyter/scipy-notebook:2026-11-23@sha256:21b93d2df02daa665b11442282d01f96d5a639e8ca9045cfd296e2896709b2fc

# The upstream startup helper fixes volume ownership, then drops to jovyan.
USER root
COPY railway-start.sh /usr/local/bin/railway-start.sh
COPY railway_server_config.py /etc/jupyter/railway_server_config.py
RUN chmod 0755 /usr/local/bin/railway-start.sh
ENV CHOWN_HOME=yes \
    CHOWN_HOME_OPTS=-R \
    PYTHONUSERBASE=/home/jovyan/.local \
    JUPYTER_RUNTIME_DIR=/tmp/jupyter-runtime
CMD ["/usr/local/bin/railway-start.sh"]
