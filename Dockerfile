FROM python:3.5

EXPOSE 5000
ENV FB_DB_HOST=postgres

RUN mkdir /srv/fb-tracker
WORKDIR /srv/fb-tracker
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY fbserver ./fbserver
COPY fbcore ./fbcore
COPY main.py ./

CMD ["python3", "main.py", "create_and_run"]
