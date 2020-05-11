FROM python:3.7
ADD . /app
COPY ./app/app.py /app/app.py
WORKDIR /app
RUN pip install -r requirements.txt
