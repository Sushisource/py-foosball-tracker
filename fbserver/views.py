import datetime

from fbserver import app
from flask import render_template, jsonify, request
from flask.ext.restful import Resource, Api, reqparse
from fbserver.database import Game, Player, db, PlayerGame, HistoricalGame
from fbcore import player_list_to_win_loss_tuple

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

card_event_parser = parser.copy()
card_event_parser.add_argument('card_id', type=str, required=True)
card_event_parser.add_argument('card_type', type=str, required=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/elm')
def elm_index():
    return render_template('elm_ix.html')


class GameR(Resource):
    def get(self, game_id):
        game = Game.query.filter_by(id=game_id).first()
        if game is None:
            return 404
        players = game.players
        retthis = {'game': game, 'players': players}
        if game.historical:
            retthis['historical_game'] = game.historical_game
        return jsonify(retthis)


class GameList(Resource):
    def get(self):
        args = parser.parse_args()
        inprog = args['inprog']
        if inprog is not None:
            games = Game.query.filter_by(inprog=inprog).all()
        else:
            games = Game.query.filter_by().all()
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
        plist = request.get_json()['player_list']

        hgame = HistoricalGame(winteam="winners")
        game = Game(date=datetime.datetime.now(), inprog=False, historical=True,
                    historical_game=hgame)
        models = [game, hgame]
        for player in plist:
            pmod = PlayerList.find_or_make_player(player['name'])
            models.append(pmod[0])
            team = "winners" if player['winner'] else "losers"
            pgame = PlayerGame(player=pmod[0], game=game, team=team)
            models.append(pgame)

        db.session.add_all(models)
        db.session.commit()
        return {'save': True}


class PlayerList(Resource):
    def get(self):
        return jsonify({'players': Player.query.all()})

    @staticmethod
    def find_or_make_player(name):
        name = name.lower()
        existing_player = Player.query.filter_by(name=name).first()
        if existing_player:
            return existing_player, True
        return Player(name=name), False

    def post(self):
        args = login_parser.parse_args()
        name = args['loginName']
        player, existed = self.find_or_make_player(name)
        if not existed:
            db.session.add(player)
            db.session.commit()
            return jsonify({'player': player})
        else:
            return jsonify({'exists': True, 'player': player})


class PlayerGameR(Resource):
    def get(self, pgid):
        pgame = PlayerGame.query.filter_by(id=pgid).first_or_404()
        return jsonify({pgame})


class PlayerGameList(Resource):
    def get(self):
        args = pgame_parser.parse_args()
        pgame = PlayerGame.query.filter_by(
            player_id=args['player_id'],
            game_id=args['game_id']).first()
        if pgame:
            return jsonify({'player_game': pgame})
        else:
            return {}

    def post(self):
        args = pgame_parser.parse_args()
        pgame = PlayerGame(player_id=args['player_id'],
                           game_id=args['game_id'],
                           team=args['team'])
        db.session.add(pgame)
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
api.add_resource(PlayerGameList, '/player_games')
api.add_resource(PlayerGameR, '/player_games/<pgid>')
api.add_resource(CardEventEndpoint, '/card')
