
FROM python:latest
RUN apt-get update -y
RUN apt-get install vim -y

# WORKDIR /usr/src/app
WORKDIR /

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install websocket-client

COPY . .

# CMD ["python","./kpi_vs_class_10_5.py"]
# ENTRYPOINT ["/bin/bash"]
# CMD ["run.sh"]
