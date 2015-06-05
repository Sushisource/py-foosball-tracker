FROM python:3.4.3

RUN pip install -r requirements.txt
# TODO: Consider running as non-root user.
WORKDIR /srv/fb-tracker

EXPOSE 5000

CMD ["python3", "main.py", "run"]
