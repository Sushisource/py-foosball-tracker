import os

from flask import Flask
from flask.json import JSONEncoder

app = Flask('fbserver')
from fbserver.database import db
import fbserver.util


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, db.Model):
            return obj.json
        return JSONEncoder.default(self, obj)


host = os.environ.get("FB_DB_HOST", 'localhost')
app.config[
    'SQLALCHEMY_DATABASE_URI'] = "postgres://foosball:foosball@{}/fbdb".format(
    host)
app.json_encoder = CustomJSONEncoder

# Create our global ranker, and Populate it with what was in the DB at
# startup time
@app.before_first_request
def init_ranker():
    fbserver.util.get_rankings_obj()

import fbserver.views
