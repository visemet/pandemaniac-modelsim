"""
Class: main.py
--------------
Main class for the epidemic model simulator. Handles input and output of files
and to the database.
"""

import argparse
import compute
import json
import os
from simulation import Simulation
import sys
import time

# Location of files.
GRAPH_FOLDER = "private/graphs/"
TEAMS_FOLDER = "private/uploads/"
OUTPUT_FOLDER = "private/runs/"

# Maximum number of generations to run the simulation.
MAX_ROUNDS = 100

# Points for places.
POINTS = {1:20, 2:15, 3:12, 4:9, 5:7, 6:5, 7:4, 8:3, 9:2, 10:1}

# Rankings.
RANKS = {}

def generate_nodes(graph, num):
  """
  Function: generate_nodes
  ------------------------
  Generate nodes for all the methods.
  """
  #compute.main(graph, num, "degree")
  #compute.main(graph, num, "closeness")
  #compute.main(graph, num, "betweenness")
  #compute.main(graph, num, "clustering")
  #compute.main(graph, num, "random")
  #compute.main(graph, num, "random2")
  compute.main(graph, num, "r-closeness")
  compute.main(graph, num, "r-betweenness")
  #compute.main(graph, num, "random3")


def create_adj_list(graph):
  """
  Function: create_adj_list
  -------------------------
  Creates the adjacency list representation of the graph from a file containing
  the graph. The file is in JSON format.

  graph: The graph to create an adjacency list for.
  returns: An adjacency list.
  """
  graph_file = open(GRAPH_FOLDER + graph, "r")
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


def update_points(f, results):
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
  # Result is a list of tuples (team, number of nodes).
  ranked_teams = [(x[0], len(x[1])) for x in results.items()]
  ranked_teams = sorted(ranked_teams, key=lambda k: k[1], reverse=True)

  # Olympic scoring.
  rank = 1
  for i in range(len(ranked_teams)):
    team = ranked_teams[i][0]
    if team not in RANKS:
      RANKS[team] = []

    # If they have the same number of nodes as the previous rank, they are
    # tied.
    if not (i > 0 and ranked_teams[i][1] == ranked_teams[i - 1][1]):
      rank = i + 1
    f.write("(" + team + ", " + str(rank) + ")\t")
    RANKS[team].append(rank)
  f.write("\n")


if __name__ == "__main__":
  # Parse the command-line arguments.
  parser = argparse.ArgumentParser(description='Get the model.')
  parser.add_argument("--model")
  parser.add_argument("--num")
  parser.add_argument("--teams", nargs='+')
  args = parser.parse_args()
  (num, model, teams) = (int(args.num), args.model, args.teams)

  # Usage message.
  if model is None:
    print "Usage: main-test.py --model [model name] --num [number of nodes]"
    sys.exit(0)

  f = open(OUTPUT_FOLDER + "_ranks.txt", "w")
  num_graphs = 0.0

  # Run the simulation for every graph.
  for graph in os.listdir(GRAPH_FOLDER):
    # Generate each team's nodes for this graph.
    generate_nodes(graph, num)
    # Create the adjacency list for the graph.
    adj_list = create_adj_list(graph)
    # Read in the node selection for each team.
    team_nodes = read_nodes(graph, adj_list.keys(), teams)

    # Run the simulation and output the run to file.
    simulation = Simulation(MAX_ROUNDS, model, team_nodes, adj_list)
    (_, results) = simulation.run()
    num_graphs += 1
    print "Processed " + str(int(num_graphs)) + " graphs."

    # Get the final results of teams to their nodes and update their points.
    update_points(f, results)

  def var(lst):
    average = sum(lst) / len(lst) * 1.0
    var = sum((average - val) ** 2 for val in lst) / len(lst)
    return var


  # Results of all runs.
  f.close()
  avg_ranks = sorted([(team, sum(ranks) / (len(ranks) * 1.0)) \
    for (team, ranks) in RANKS.items()], \
    key=lambda x: x[1])
  var_ranks = sorted([(team, var(ranks)) for (team, ranks) in RANKS.items()], \
    key=lambda x: x[1], reverse=True)
  print "\nAverage Rank:", str(avg_ranks)
  print "\nVariance of Rank:", str(var_ranks),
