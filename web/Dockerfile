FROM python:3.8-slim

RUN apt-get update && apt-get install -y \
    tzdata \
&& rm -rf /var/lib/apt/lists/*

WORKDIR /tmp/work

ENV TZ=Asia/Tokyo
