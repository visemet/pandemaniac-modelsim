from CONFIG import *
from match import get_match
from main import do_main, get_graph

import argparse
import json
import os
import random

def create_random_team(graph, num_nodes, name):
  # Open graph file and get random nodes.
  graph_file = open(GRAPH_FOLDER + get_graph(graph), "r")
  adj_list = json.loads("".join(graph_file.readlines()))
  graph_file.close()
  nodes = random.sample(adj_list.keys(), num_nodes)

  # Write out to file.
  if not os.path.exists(TEAMS_FOLDER + name):
    os.makedirs(TEAMS_FOLDER + name)
  output = open(TEAMS_FOLDER + name + "/" + graph + "-" + str(num_nodes), "w")
  for node in nodes:
    output.write(str(node) + "\n")
  output.close()


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  # Day of the practice rounds or competition.
  parser.add_argument("--day")
  parser.add_argument("--teams", nargs="+")
  args = parser.parse_args()
  (day, orig_teams) = (args.day, args.teams)

  config = DAYS[day]
  # Loop through each graph for this day/competition round.
  for (graph, num_teams, num_nodes) in config:
    teams = [x for x in orig_teams]
    # If this is a one-on-one with a TA team.
    if type(num_teams) == str:
      ta_team = num_teams
      for team in teams: 
        do_main(graph, [team, ta_team], "majority_colored")

    # Otherwise match just the student teams.
    else:
      # If there aren't enough teams to play on this graph, create random
      # teams.
      if len(teams) < num_teams:
        for i in range(num_teams - len(teams)):
          create_random_team(graph, num_nodes, "filler" + str(i + 1))
          teams.append("filler" + str(i + 1))
      matches = get_match(num_teams, teams)
      for match in matches:
        do_main(graph, match, "majority_colored")
