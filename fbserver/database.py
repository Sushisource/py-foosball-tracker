from fbserver import app
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)
# must import models
from fbserver.models import *


def drop_all():
    db.drop_all()


def create_all():
    print("Creating db/tables")
    db.create_all(app=app)
    print("Created")
    db.session.commit()


def remove_session():
    db.session.remove()
