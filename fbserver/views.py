from fbserver import app
from flask import render_template, jsonify
from flask.ext.restful import Resource, Api, reqparse
from fbserver.database import Game, Player, db, PlayerGame
import datetime

api = Api(app)
parser = reqparse.RequestParser()
parser.add_argument('limit', type=int)
parser.add_argument('inprog', type=str)

login_parser = parser.copy()
login_parser.add_argument('loginName', type=str, required=True)

pgame_parser = parser.copy()
pgame_parser.add_argument('game_id', type=int, required=True)
pgame_parser.add_argument('player_id', type=int, required=True)
pgame_parser.add_argument('team', type=str)


@app.route('/')
def index():
    return render_template('index.html')


class GameR(Resource):
    def get(self, game_id):
        pass


class GameList(Resource):
    def get(self):
        args = parser.parse_args()
        inprog = args['inprog']
        games = Game.query.filter_by(inprog=inprog).all()
        return jsonify({'games': games})

    def post(self):
        args = parser.parse_args()
        inprog = args.get('inprog', False)
        nugame = Game(inprog=inprog, date=datetime.datetime.now())
        db.session.add(nugame)
        db.session.commit()
        return jsonify({'game': nugame})


class HistoricalGameList(Resource):
    def post(self):
        args = parser.parse_args()


class PlayerList(Resource):
    def get(self):
        return jsonify({'players': Player.query.all()})

    def post(self):
        args = login_parser.parse_args()
        name = args['loginName']
        existing_player = Player.query.filter_by(name=name).first()
        if not existing_player:
            nuplayer = Player(name=name)
            db.session.add(nuplayer)
            db.session.commit()
            return jsonify({'player': nuplayer})
        else:
            return jsonify({'exists': True, 'player': existing_player})


class PlayerGameR(Resource):
    def get(self, pgid):
        pgame = PlayerGame.query.filter_by(id=pgid).first_or_404()
        return jsonify(pgame)


class PlayerGameList(Resource):
    def get(self):
        args = pgame_parser.parse_args()
        pgame = PlayerGame.query.filter_by(
            player_id=args['player_id'],
            game_id=args['game_id']).first()
        if pgame:
            return jsonify(pgame)
        else:
            return {}

    def post(self):
        args = pgame_parser.parse_args()
        pgame = PlayerGame(player_id=args['player_id'],
                           game_id=args['game_id'],
                           team=args['team'])
        db.session.add(pgame)
        db.session.commit()


api.add_resource(GameR, '/games/<game_id>')
api.add_resource(GameList, '/games')
api.add_resource(HistoricalGameList, '/historical_games')
api.add_resource(PlayerList, '/players')
api.add_resource(PlayerGameList, '/player_games')
api.add_resource(PlayerGameR, '/player_games/<pgid>')
