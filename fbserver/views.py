from fbserver import app
from flask import render_template
from flask.ext.restful import Resource, Api, reqparse
from fbserver.database import Game, Player, db

api = Api(app)
parser = reqparse.RequestParser()
parser.add_argument('limit', type=int)
parser.add_argument('inprog', type=str)

login_parser = parser.copy()
login_parser.add_argument('loginName', type=str, required=True)


@app.route('/')
def index():
    return render_template('index.html')


class GameR(Resource):
    def get(self, game_id):
        pass


class GameList(Resource):
    def get(self):
        args = parser.parse_args()
        print(args)
        games = Game.query.all()
        return {'games': games}

    def post(self):
        args = parser.parse_args()


class HistoricalGameList(Resource):
    def post(self):
        args = parser.parse_args()
        print(args)


class PlayerList(Resource):
    def get(self):
        return {'players': [p.json for p in Player.query.all()]}

    def post(self):
        args = login_parser.parse_args()
        name = args['loginName']
        existing_player = Player.query.filter_by(name=name).first()
        if not existing_player:
            nuplayer = Player(name=name)
            db.session.add(nuplayer)
            db.session.commit()
            return {'player': nuplayer.json}
        else:
            return {'exists': True, 'player': existing_player.json}


api.add_resource(GameR, '/games/<game_id>')
api.add_resource(GameList, '/games')
api.add_resource(HistoricalGameList, '/historical_games')
api.add_resource(PlayerList, '/players')
