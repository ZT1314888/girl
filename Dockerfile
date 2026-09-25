FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/

COPY <<'CRONTAB' /etc/cron.d/girl-cron
5 18 * * * cd /app && /usr/local/bin/python -m app.main >> /var/log/girl.log 2>&1
CRONTAB

RUN chmod 0644 /etc/cron.d/girl-cron && crontab /etc/cron.d/girl-cron

CMD ["cron", "-f"]
