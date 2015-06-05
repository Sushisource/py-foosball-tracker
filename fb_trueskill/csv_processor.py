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
from ranker import TotalRanking


class CSVProcessor:
    players = set()
    records = []

    def __init__(self, csv_filepath):
        with open(csv_filepath, newline='') as csvf:
            rdr = csv.reader(csvf)
            for row in rdr:
                if not row:
                    continue
                [self.players.add(x.strip()) for x in row]
                self.records.append(row)


if __name__ == "__main__":
    csvp = CSVProcessor(sys.argv[1])

    print(csvp.players)

    ranker = TotalRanking()
    for player in csvp.players:
        ranker.add_player(player)

    for record in csvp.records:
        t1 = [record[0].strip(), record[1].strip()]
        t2 = [record[2].strip(), record[3].strip()]
        ranker.process_game_record(t1, t2)

    print("Total games: {}".format(ranker.total_games))
    for player in ranker.player_rankings():
        print(player)
