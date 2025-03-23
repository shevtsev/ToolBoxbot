FROM python

WORKDIR /apps
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt
COPY ToolBox /apps/ToolBox
COPY UsersData.db .

ENTRYPOINT ["python", "ToolBox/ToolBox_main.py"]