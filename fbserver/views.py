from flask import render_template
from flask.ext.restful import Resource, Api, reqparse

from fbserver import app
from fbserver.database import Game, Player, db


api = Api(app)
parser = reqparse.RequestParser()
parser.add_argument('limit', type=int)
parser.add_argument('inprog', type=str)

login_parser = parser.copy()
login_parser.add_argument('loginName', type=str, required=True)

card_event_parser = reqparse.RequestParser()
card_event_parser.add_argument('card_id', type=str, required=True)
card_event_parser.add_argument('card_type', type=str, required=True)


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
        print(args)
        name = args['loginName']
        if not Player.query.filter_by(name=name).first():
            nuplayer = Player(name=name)
            db.session.add(nuplayer)
            db.session.commit()


class CardEventEndpoint(Resource):
    # Non-functioning
    def post(self):
        args = card_event_parser.parse_args()
        print(args)
        print("Card Event: {card_id}/{card_type}".format(**args))
        return {'status': 'ok'}


api.add_resource(GameR, '/games/<game_id>')
api.add_resource(GameList, '/games')
api.add_resource(HistoricalGameList, '/historical_games')
api.add_resource(PlayerList, '/players')
api.add_resource(CardEventEndpoint, '/card')
