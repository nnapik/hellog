FROM python:3-alpine

RUN apt update && apt upgrade && apt install libffi-dev python3-dev ffmpeg
RUN python3 -m pip install -U discord.py discord.pyvoice PyNaCl youtube_dl
ENV BOT_SECRET=""
COPY bot.py ./

ENTRYPOINT ["python3", "bot.py"]
