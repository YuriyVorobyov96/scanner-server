FROM python:3.12-rc-bookworm

RUN apt-get update && \
        apt-get install -y iputils-ping

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY scanner_server.py scanner_server.py

EXPOSE 3000

CMD [ "python3", "scanner_server.py" ]
