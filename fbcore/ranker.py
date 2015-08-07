"""
For running over game records to produce trueskill rankings
"""
from trueskill import rate, TrueSkill
import threading


class TotalRanking:
    __instance = None
    lock = threading.Lock()

    @classmethod
    def instance(cls):
        if not cls.__instance:
            with cls.lock:
                if not cls.__instance:
                    cls.__instance = cls()
        return cls.__instance

    def __init__(self):
        # All the Players involved in this ranking. Maps player names to
        # Ratings.
        self.players = dict()
        # The TrueSkill environment
        self.ts_env = TrueSkill()
        self.total_games = 0

    def add_player(self, player_name):
        """
        Add a player to this raking. Players must have unique, consistent
        names.

        :param player_name: The player name
        """
        if player_name not in self.players:
            self.players[player_name] = self.ts_env.create_rating()

    def process_game_record(self, team1, team2):
        """
        Process a game, and update the rankings accordingly. Team 1 is the
        winning team.
        TODO: Update to include 3-team (KoTH)

        :param team1: A list of player names on team one. Can contain one
            player
        :param team2: A list of player names on team two. Can contain one
            player
        """
        if not isinstance(team1, list) or not isinstance(team2, list):
            raise ValueError("Arguments must be lists of players")

        for player in team1 + team2:
            self.add_player(player)

        try:
            t1_ratings = {p: self.players[p] for p in team1}
            t2_ratings = {p: self.players[p] for p in team2}
        except KeyError as e:
            raise ValueError("Could not find a player: {}".format(e))

        new_rankings = self.ts_env.rate([t1_ratings, t2_ratings])
        for team in new_rankings:
            for name, newrating in team.items():
                self.players[name] = newrating
        self.total_games += 1

    def player_rankings(self):
        """
        :return: Players, with their rankings, sorted by rank.
        """
        ranks = [(p, r) for p, r in self.players.items()]
        ranks = sorted(ranks, key=lambda pr: self.ts_env.expose(pr[1]),
                       reverse=True)
        return ranks
