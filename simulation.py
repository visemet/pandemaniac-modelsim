"""
Class: simulation.py
--------------------
Contains functions involving the simulation and the generations in the
simulation.
"""

from collections import Counter, OrderedDict
from copy import deepcopy
import models

# Maximum number of rounds to run the simulation.
MAX_ROUNDS = 100

def run(team_nodes, adj_list):
  """
  Function: run
  -------------
  Runs the epidemic simulation for each round of the epidemic until there is
  no more spread (i.e. it is stable) or we reach the maximum number of rounds.

  team_nodes: The dictionary containing a mapping of a team name and the nodes
              they chose.
  adj_list: The adjacency list representation of the graph.

  returns: A tuple (output, results) where the output is a dictionary object
           containing a mapping of each generation to the diffs generated and
           the results is the final mapping of teams to their nodes.
  """

  # Stores a mapping of nodes to their team.
  node_team = dict([(node, None) for node in adj_list])
  # Output to be written to file.
  output = OrderedDict()

  # Choose the initial generation of nodes. The model can be changed.
  diff = models.init_conflict(team_nodes, node_team)
  output["0"] = to_team_mapping(diff)
  generation = 1

  # Keep calculating the epidemic until it stops changing.
  while not is_stable(generation, output):
    print "Generation:", str(generation)
    diff = {}
    node_team_copy = deepcopy(node_team)
    # Find the new color for every node. The model can be changed.
    for node in adj_list:
      (changed, color) = models.next_random_weighing(adj_list, node_team, node)
      # Store the node's new color only if it changed.
      if changed:
        diff[node] = color
        node_team_copy[node] = color
    node_team = node_team_copy

    # Convert the mapping of a node to the team into teams and their nodes.
    output[str(generation)] = to_team_mapping(diff)
    generation += 1

  return (output, to_team_mapping(node_team))


def is_stable(generation, output):
  """
  Function: is_stable
  -------------------
  Checks to see if the graph is still changing by comparing the current
  generation's node-to-team mappings with the previous generation's.

  generation: The current generation.
  output: The list of generations, teams, and their nodes.
  returns: True if the graph is stable, False otherwise.
  """

  # If this is the initial generation, nothing to check yet.
  if generation <= 1:
    return False

  # If we have reached the maximum number of rounds, then stop.
  if generation == MAX_ROUNDS:
    return True

  current = output[str(generation - 1)]
  previous = output[str(generation - 2)]

  for team in current.keys():
    # If the two lists don't have the same elements.
    compare_lists = lambda x, y: Counter(x) == Counter(y)
    if not compare_lists(current[team], previous[team]):
      return False

  return True


def to_team_mapping(diff):
  """
  Function: to_team_mapping
  -------------------------
  Converts a dictionary from node -> team to team -> nodes.

  diff: The dictionary to convert.
  returns: A new dictionary containing a mapping of teams to their nodes.
  """
  team_nodes = {}
  for node, team in diff.items():
    # Ignore conflicts.
    if team == "__CONFLICT__":
      continue
    if team in team_nodes:
      team_nodes[team].append(node)
    else:
      team_nodes[team] = [node]
  return team_nodes
