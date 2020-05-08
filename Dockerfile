FROM python:3.7
ADD . /app
WORKDIR /
RUN pip install -r requirements.txt
