FROM python:3.12-alpine

WORKDIR /home/cloud_app

COPY ../requirements.txt .

RUN python -m pip install -r requirements.txt

COPY ../app/ ./app/
COPY ../run.py .

EXPOSE 5000

CMD [ "pyhton", "run.py"]
