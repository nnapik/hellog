FROM python:buster

RUN echo "Acquire::http::No-Cache true;" > /etc/apt/apt.conf \
    && echo "Acquire::http::Pipeline-Depth 0;" >> /etc/apt/apt.conf \
    && apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y libffi-dev python3-dev ffmpeg

RUN python3 -m pip install --upgrade pip && python3 -m pip install -U discord.py PyNaCl youtube_dl boto3
#RUN apk del .build-deps gcc musl-dev make
ENV BOT_SECRET=changeme

COPY *.py ./
COPY cogs ./cogs

ENTRYPOINT ["python3", "bot.py"]

