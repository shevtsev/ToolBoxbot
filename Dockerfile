FROM python:3.12

WORKDIR /apps

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "ToolBox/ToolBox_main.py"]