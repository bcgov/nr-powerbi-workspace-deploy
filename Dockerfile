FROM python

RUN pip install boto3 requests

COPY app/main.py /usr/bin/main.py

COPY app/entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]