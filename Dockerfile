FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /dns_backup/ && chmod 755 /dns_backup/ && \
    groupadd -g 10000 app && useradd -u 10000 -g 10000 app

USER app

COPY . /dns_backup/

WORKDIR /dns_backup/
