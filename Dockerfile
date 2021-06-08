FROM python:slim-buster
WORKDIR /flaskAPI
COPY requirements.txt /flaskAPI/
RUN pip install -r requirements.txt --no-cache-dir
COPY . /flaskAPI/
ENV FLASK_APP flaskAPI.py
CMD flask run --host=0.0.0.0