from fbcore.ranker import TotalRanking
from fbserver.models import HistoricalGame

__author__ = 'sjudge'


def get_rankings():
    rankings = get_rankings_obj()
    return rankings.player_rankings()


def get_rankings_obj():
    tr = TotalRanking.instance()
    all_games = HistoricalGame.query.all()
    print("Initting rankings...")
    for hgame in all_games:
        winners, losers = game_to_winners_losers(hgame.game)
        tr.process_game_record(winners, losers)
    return tr


def game_to_winners_losers(game):
    winners = [p.name for p in game.winners]
    losers = [p.name for p in game.losers]
    return winners, losers
