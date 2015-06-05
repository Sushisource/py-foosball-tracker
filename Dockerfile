FROM python:3.4.3

# TODO: Consider running as non-root user.
RUN mkdir /srv/fb-tracker
WORKDIR /srv/fb-tracker
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY * ./

EXPOSE 5000

CMD ["python3", "main.py", "run"]
