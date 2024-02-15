FROM python:alpine

RUN deps='gcc python3-dev musl-dev' \
    && apk update \
    && apk add --no-cache libpq \
    && apk add --virtual temp1 --no-cache $deps \
    && pip install boto3 \
    && pip install requests \
    && apk del temp1

ADD *.py .

CMD ["python3", "./main.py"]