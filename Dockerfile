FROM python:3.9-rc-buster

RUN apt-get update && apt-get upgrade -y && apt-get install -y libffi-dev python3-dev ffmpeg
#RUN apk update && apk add libffi-dev python3-dev ffmpeg
#RUN apk add --no-cache --virtual .build-deps gcc musl-dev make
RUN python3 -m pip install --upgrade pip && python3 -m pip install -U discord.py PyNaCl youtube_dl
#RUN apk del .build-deps gcc musl-dev make
ENV BOT_SECRET=

COPY *.py ./
COPY cogs ./cogs

ENTRYPOINT ["python3", "bot.py"]

