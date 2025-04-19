FROM python

WORKDIR /apps
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt

COPY ToolBox /apps/ToolBox
COPY UsersData.db .

# Создаем конфигурацию supervisor
RUN echo '[supervisord]\n\
nodaemon=true\n\
\n\
[program:toolbox]\n\
command=python ToolBox/ToolBox_main.py\n\
directory=/apps\n\
autostart=true\n\
autorestart=true\n\
stderr_logfile=/var/log/toolbox.err.log\n\
stdout_logfile=/var/log/toolbox.out.log\n\
environment=PYTHONUNBUFFERED=1' > /etc/supervisor.conf

# Меняем точку входа на supervisor
ENTRYPOINT ["supervisord", "-c", "/etc/supervisor.conf"]