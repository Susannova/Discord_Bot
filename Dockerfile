FROM python:3.11-bookworm

WORKDIR /usr/src/Discord_Bot

COPY . .
RUN apt update
RUN apt install libffi-dev libnacl-dev -y
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./discord_bot.py" ]
