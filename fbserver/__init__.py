from flask import Flask

app = Flask('fbserver')
app.config[
    'SQLALCHEMY_DATABASE_URI'] = "postgres://foosball:foosball@sjudge/foosball"

import fbserver.views
