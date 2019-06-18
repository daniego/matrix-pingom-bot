FROM python:3.6-slim

COPY ["requirements.txt", "/srv/matrix_pingdom_bot/"]
WORKDIR /srv/matrix_pingdom_bot/
RUN python3 -m venv /opt/pingdom_matrix_bot && \
    /opt/pingdom_matrix_bot/bin/pip install -r requirements.txt && \
#
    echo "source /opt/pingdom_matrix_bot/bin/activate" >> /root/.bashrc && \
    echo 'PS1="\u@\h::\W# "' >> ~/.bashrc && \
#
    apt-get update && \
    apt-get install --no-install-recommends -y \
      nginx \
      curl && \
#
    rm -f /etc/nginx/sites-enabled/default && \
#
    apt-get autoremove -y && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/*

COPY container_fs /
COPY ["matrix_pingdom_bot.py", "settings.py", "/srv/matrix_pingdom_bot/"]
COPY templates /srv/matrix_pingdom_bot/templates

ENTRYPOINT ["/opt/pingdom_matrix_bot/bin/supervisord", "-c", "/etc/supervisord.conf", "-n"]
