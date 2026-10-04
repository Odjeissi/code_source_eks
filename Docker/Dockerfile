FROM python:3.12-alpine

WORKDIR /home/cloud_app

COPY ../requirements.txt .

RUN python -m pip install --no-cache-dir -r requirements.txt

COPY ../app/ ./app/
COPY ../run.py .

# create the group and non-root user
RUN addgroup -g 1000 appgroup \
    && adduser -u 1000 -G appgroup -D appuser

# Give appuser ownership
RUN chown -R appuser:appgroup /home/cloud_app

USER appuser

EXPOSE 5000

CMD [ "python", "run.py" ]
