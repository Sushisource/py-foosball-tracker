"""
Trueskill processor for CSV files. CSV files shall be of the format:

player1_name, player2_name, player3_name, player4_name

If only two players are present, player 1 wins. If three players are present,
player 1 wins, player 2 was second. If all four are present, the team composed
of player 1 and player 2 wins, with player 3 and player 4 being on the losing
team.
"""
import csv
import sys
import os
import argparse
import json
# No clue why python is being an asshole about this
sys.path.append(os.getcwd())
from fbcore import player_list_to_win_loss_tuple
from fbcore.ranker import TotalRanking
import requests


class CSVProcessor:
    players = set()
    records = []

    def __init__(self, csv_filepath):
        with open(csv_filepath, newline='') as csvf:
            rdr = csv.reader(csvf)
            for row in rdr:
                if not row:
                    continue
                [self.players.add(x.strip().lower()) for x in row]
                self.records.append(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file")
    parser.add_argument("-p", "--post-to-srv", action="store_true", dest="post")
    args = parser.parse_args()

    csvp = CSVProcessor(args.csv_file)

    print(csvp.players)

    ranker = TotalRanking()
    for player in csvp.players:
        ranker.add_player(player)

    for record in csvp.records:
        wl_tup = player_list_to_win_loss_tuple(record)
        load = [{'name': p, 'winner': True} for p in wl_tup[0]]
        load += [{'name': p, 'winner': False} for p in wl_tup[1]]
        ranker.process_game_record(*wl_tup)
        if args.post:
            load = {'player_list': load}
            headers = {'Content-type': 'application/json'}
            r = requests.post("http://localhost:5000/historical_games",
                              data=json.dumps(load), headers=headers)

    print("Total games: {}".format(ranker.total_games))
    for player in ranker.player_rankings():
        print(player)
