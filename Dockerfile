FROM python:3.4.3

EXPOSE 5000

RUN mkdir /srv/fb-tracker
WORKDIR /srv/fb-tracker
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY fbserver ./fbserver
COPY fb_trueskill ./fb_trueskill
COPY main.py ./

RUN ["ls", "-la", "."]
CMD ["python3", "main.py", "run"]
