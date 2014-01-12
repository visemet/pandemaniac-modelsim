"""
Class: main.py
--------------
Main class for the epidemic model simulator. Handles input and output of files
and to the database.
"""

import argparse
import json
import os
from pymongo import MongoClient
import sys
import time

from CONFIG import *
from simulation import Simulation

db = MongoClient(DB_SERVER, DB_PORT)

def get_graph(graph):
  """
  Function: get_graph
  -------------------
  Gets the actual file name of the graph specified by graph.
  """
  f = db.test.graphs.find_one({ "name" : graph })
  if f is not None:
    return f["file"]
  return None


def create_adj_list(graph):
  """
  Function: create_adj_list
  -------------------------
  Creates the adjacency list representation of the graph from a file containing
  the graph. The file is in JSON format.

  graph: The graph to create an adjacency list for.
  returns: An adjacency list.
  """
  graph_file = open(GRAPH_FOLDER + get_graph(graph), "r")
  adj_list = json.loads("".join(graph_file.readlines()))
  # Convert the values to strings.
  for key in adj_list.keys():
    adj_list[key] = [str(x) for x in adj_list[key]]
  graph_file.close()
  return adj_list


def read_nodes(graph, valid_nodes, teams):
  """
  Function: read_nodes
  --------------------
  Reads in the node selection for a team and creates a mapping of the team to
  the nodes they chose.

  graph: The corresponding graph.
  teams: The list of teams.
  returns: A dictionary containing the key as the team and the value as the
           list of chosen nodes.
  """
  team_nodes = {}
  for team in teams:
    # Gets this team's submission by getting the most recent submission for
    # this particular graph.
    team_dir = TEAMS_FOLDER + team + "/"
    try:
      team_file_name = max([f for f in os.listdir(team_dir) \
        if f.startswith(graph + "-")])
      team_file = open(team_dir + team_file_name, "r")

      # Read in all of the nodes and filter out spaces and newlines.
      nodes = filter(lambda x: x, \
        [x.strip().replace("\r", "") for x in team_file.read().split("\n")])
      team_file.close()

      # The list of nodes a team submits should now be valid.
      is_valid = reduce(lambda x, node: x and (node in valid_nodes), nodes)
      if is_valid:
        team_nodes[team] = nodes
      else:
        print "Nodes for team " + team + " are not valid."

    # If no file is found, then this team did not have a submission. They do
    # not get any nodes.
    except (OSError, Exception, ValueError):
      team_nodes[team] = []

  return team_nodes


def update_points(results):
  """
  Function: update_points
  -----------------------
  Update the results of this run.

  results: The results of this run. Is a dictionary with the keys as the teams
           and values as the nodes for that team. Computes the number of points
           each team gets by the number of nodes they have.
  """

  # Put the teams in order of number of nodes they have, sorted most to least.
  # Result is a list of tuples (team, number of nodes).
  ranked_teams = [(x[0], len(x[1])) for x in results.items()]
  ranked_teams = sorted(ranked_teams, key=lambda k: k[1], reverse=True)

  # Olympic scoring. Add the score to the database.
  scores = {}
  rank = 1
  for i in range(len(ranked_teams)):
    (team, num) = ranked_teams[i]
    # If they have the same number of nodes as the previous rank, they are
    # tied. They get the same points as the previous team.
    if not (i > 0 and num == ranked_teams[i - 1][1]):
      rank = i + 1
    # Teams that didn't get any nodes get a score of 0.
    scores[team] = (POINTS[rank] if num > 0 else 0)

  return scores


def do_main(graph, teams, model):
  print "\n\nGraph:", graph, "  Teams:", teams

  # Create the adjacency list for the graph.
  adj_list = create_adj_list(graph)
  # Read in the node selection for each team.
  team_nodes = read_nodes(graph, adj_list.keys(), teams)

  # Run the simulation and output the run to file.
  simulation = Simulation(MAX_ROUNDS, model, team_nodes, adj_list)
  (output, results) = simulation.run()
  output_filename = graph + "-" + str(time.time()) + ".txt"
  output_file = open(OUTPUT_FOLDER + output_filename, "w")
  output_file.write(str(json.dumps(output)))
  output_file.close()

  # Get the final results of teams to their nodes and update their points in
  # the database.
  scores = update_points(results)
  db.test.runs.insert({ \
    "teams": teams, \
    "scores": scores, \
    "graph": graph, \
    "file": output_filename \
  })


if __name__ == "__main__":
  # Parse the command-line arguments to get the graph and teams participating.
  parser = argparse.ArgumentParser(description='Get the graph and teams.')
  parser.add_argument("--graph")
  parser.add_argument("--teams", nargs='+')
  parser.add_argument("--model")
  args = parser.parse_args()
  (graph, teams, model) = (args.graph, args.teams, args.model)

  # Usage message.
  if graph is None or teams is None or model is None:
    print "Usage: main.py --graph [graph name] --teams " + \
      "[list of team names] --model [model name]"
    sys.exit(0)

  do_main(graph, teams, model)
