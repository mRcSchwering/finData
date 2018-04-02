# main language
FROM python:3.5-slim

# the code
WORKDIR /app
ADD . /app

# needed by circleci
RUN apt-get update && apt-get install -y git ssh

# python requirements
RUN pip3 install -r requirements.txt
