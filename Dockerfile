FROM quay.io/jupyter/scipy-notebook:2026-09-07@sha256:ec7343ba248a7473c42322e86e7157bef9ebc9253c40a88e573b3fcf607a9a8a

# The inherited entrypoint fixes volume ownership, then drops to jovyan.
USER root
COPY railway-start.sh /usr/local/bin/railway-start.sh
COPY railway_server_config.py /etc/jupyter/railway_server_config.py
RUN chmod 0755 /usr/local/bin/railway-start.sh
ENV CHOWN_HOME=yes \
    CHOWN_HOME_OPTS=-R \
    PYTHONUSERBASE=/home/jovyan/.local \
    JUPYTER_RUNTIME_DIR=/tmp/jupyter-runtime
CMD ["/usr/local/bin/railway-start.sh"]
