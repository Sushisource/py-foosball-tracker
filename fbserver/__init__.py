from flask import Flask
from flask.json import JSONEncoder

app = Flask('fbserver')
from fbserver.database import db


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, db.Model):
            return obj.json
        return JSONEncoder.default(self, obj)


app.config[
    'SQLALCHEMY_DATABASE_URI'] = "postgres://foosball:foosball@localhost/fbdb"
app.json_encoder = CustomJSONEncoder

import fbserver.views
