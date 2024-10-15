FROM python:3

WORKDIR /usr/src/Discord_Bot

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./discord_bot.py" ]
