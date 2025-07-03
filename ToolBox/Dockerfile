FROM python:3.12

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p db_data
RUN mv UsersData.db db_data/
RUN mkdir -p promocodes
RUN mv BaseSettings/promocodes.json promocodes/

CMD ["python", "ToolBox_main.py"]