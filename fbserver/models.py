from fbserver.database import db


class Serializeable(object):
    # Add in serialization
    @property
    def json(self):
        return dict(self.todict())

    def todict(self):
        for c in self.__table__.columns:
            value = getattr(self, c.name)

            yield (c.name, value)


class PlayerGame(db.Model, Serializeable):  # Association table
    __tablename__ = "player_games"
    id = db.Column(db.Integer, primary_key=True)
    team = db.Column(db.String, nullable=False)

    player_id = db.Column(db.Integer, db.ForeignKey('players.id'))
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'))
    player = db.relationship("Player")
    scores = db.relationship("Score", backref="player_game")


class Game(db.Model, Serializeable):
    __tablename__ = "games"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    inprog = db.Column(db.Boolean)
    historical = db.Column(db.Boolean)

    historical_game = db.relationship("HistoricalGame", uselist=False,
                                      backref="game")
    player_games = db.relationship("PlayerGame", backref="game")

    @property
    def players(self):
        return list(map(lambda pg: pg.player, self.player_games))

    @property
    def winners(self):
        retme = []
        for pgame in self.player_games:
            if pgame.team == self.historical_game.winteam:
                retme.append(pgame.player)
        return retme

    @property
    def losers(self):
        retme = []
        for pgame in self.player_games:
            if pgame.team != self.historical_game.winteam:
                retme.append(pgame.player)
        return retme


class HistoricalGame(db.Model, Serializeable):
    __tablename__ = "historical_games"
    id = db.Column(db.Integer, primary_key=True)
    winscore = db.Column(db.Integer)
    loserscore = db.Column(db.Integer)
    # Winteam should be the player name if this was a KotH game.
    winteam = db.Column(db.String, nullable=False)

    game_id = db.Column(db.Integer, db.ForeignKey('games.id'))


class Player(db.Model, Serializeable):
    __tablename__ = "players"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    aliases = db.relationship("PlayerAlias", backref='player')


class PlayerAlias(db.Model, Serializeable):
    __tablename__ = 'aliases'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    player_id = db.Column(db.ForeignKey("players.id"))


class Score(db.Model, Serializeable):
    __tablename__ = "scores"
    id = db.Column(db.Integer, primary_key=True)
    player_game_id = db.Column(db.ForeignKey('player_games.id'))


class Card(db.Model, Serializeable):
    __tablename__ = "cards"
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(length=12), unique=True, nullable=False)
    type_id = db.Column(db.ForeignKey("card_types.id"), nullable=False)
    entity_id = db.Column(db.Integer)


class CardType(db.Model, Serializeable):
    __tablename__ = "card_types"
    id = db.Column(db.Integer, primary_key=True)
    card_type = db.Column(db.String, nullable=False, unique=True)
    cards = db.relationship("Card", backref="card_type")
