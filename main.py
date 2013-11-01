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
from simulation import Simulation
import sys
import time

# Location of files.
GRAPH_FOLDER = "private/graphs/"
TEAMS_FOLDER = "private/uploads/"
OUTPUT_FOLDER = "private/runs/"

# MongoDB configuration.
DB_SERVER = "localhost"
DB_PORT = 27017

# Maximum number of generations to run the simulation.
MAX_ROUNDS = 100

# Points for places.
POINTS = {1:20, 2:15, 3:12, 4:9, 5:7, 6:5, 7:4, 8:3, 9:2, 10:1}

def create_adj_list(graph):  
  """
  Function: create_adj_list
  -------------------------
  Creates the adjacency list representation of the graph from a file containing
  the graph. The file is in JSON format.

  graph: The graph to create an adjacency list for.
  returns: An adjacency list.
  """
  graph_file = open(GRAPH_FOLDER + graph + ".txt", "r")
  adj_list = json.loads("".join(graph_file.readlines()))
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
      nodes = filter(lambda x: x.strip(), team_file.read().split("\n"))
      team_file.close()

      # The list of nodes a team submits should now be valid.
      is_valid = reduce(lambda x, node: x and (node in valid_nodes), nodes)
      if is_valid:
        team_nodes[team] = nodes
      else:
        raise Exception("Nodes for team " + team + " are not valid.")

    # If no file is found, then this team did not have a submission. They do
    # not get any nodes.
    except OSError:
      team_nodes[team] = []

  return team_nodes


def update_points(results, db):
  """
  Function: update_points
  -----------------------
  Update the results of this run.

  results: The results of this run. Is a dictionary with the keys as the teams
           and values as the nodes for that team. Computes the number of points
           each team gets by the number of nodes they have.
  db: The client for the MongoDB connection.
  """

  # Put the teams in order of number of nodes they have, sorted most to least.
  del results[None]
  ranked_teams = sorted(results, key=lambda k: len(results[k]), reverse=True)

  # Olympic scoring. Add the score to the database.
  for i in range(1, len(ranked_teams) + 1):
    db.test.ranks.update( \
      {"team": ranked_teams[i - 1]}, \
      {"$inc": {"score": POINTS[i]}}, upsert=True)

  print str(ranked_teams)


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
    print "Usage: main.py --graph [graph name] --teams [list of team names] --model [model name]"
    sys.exit(0)

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

  # Connect to MongoDB to store results.
  db = MongoClient(DB_SERVER, DB_PORT)
  db.test.attempts.update( \
    {"graph": graph, "team": {"$in": teams}}, \
    {"$set": {"file": output_filename}}, multi=True)

  # Get the final results of teams to their nodes and update their points in
  # the database.
  update_points(results, db)
  print str(results)
