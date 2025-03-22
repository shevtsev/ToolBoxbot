FROM python:3.14.0a6-bullseye

WORKDIR /apps
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt
COPY ToolBox /apps/ToolBox

ENTRYPOINT ["python", "ToolBox/ToolBox_main.py"]