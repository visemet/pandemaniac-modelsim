# Usage:
#   python sim.py --graph [graph file name] --files [file(s) with nodes]
# Example:
#   python sim.py --graph 4.1.2.json --files test1 test2.txt
#
# Prints out the file and the number of nodes they got.

from collections import Counter, OrderedDict
from copy import deepcopy
from random import randint

import argparse
import json
import sys

def create_adj_list(graph):
  """
  Function: create_adj_list
  -------------------------
  Creates the adjacency list representation of the graph from a file
  containing the graph. The file is in JSON format.
  """
  graph_file = open(graph, "r")
  adj_list = json.load(graph_file)
  graph_file.close()
  return adj_list


def read_nodes(files):
  """
  Function: read_nodes
  --------------------
  Reads a list of files for nodes and creates a dictionary mapping the file
  name to the nodes in that file.
  """
  node_mappings = {}
  for f in files:
    fopen = open(f, 'r')
    # Filter out spaces and newlines.
    nodes = filter(lambda x: x, \
      [x.strip().replace("\r", "") for x in fopen.read().split("\n")])
    fopen.close()
    node_mappings[f] = nodes

  return node_mappings


def run_simulation(adj_list, node_mappings):
  """
  Function: run_simulation
  ------------------------
  Runs the simulation. Returns a dictionary with the
  """
  # Stores a mapping of nodes to their color.
  node_color = dict([(node, None) for node in adj_list.keys()])
  init(node_mappings, node_color)
  generation = 1

  # Keep calculating the epidemic until it stops changing.
  prev = None
  nodes = adj_list.keys()
  while not is_stable(generation, randint(100, 200), prev, node_color):
    prev = deepcopy(node_color)
    for node in nodes:
      (changed, color) = update(adj_list, prev, node)
      # Store the node's new color only if it changed.
      if changed: node_color[node] = color
    # NOTE: Could check prev and node_colors here if you want intermediate
    # steps.
    generation += 1

  return get_result(node_mappings.keys(), node_color)


def init(color_nodes, node_color):
  for (color, nodes) in color_nodes.items():
    for node in nodes:
      # More than one color has been selected for a node. They cancel out.
      if node_color[node] is not None:
        node_color[node] = "__CONFLICT__"
      else:
        node_color[node] = color
  # Now set all the conflicts back to None since those nodes don't get any
  # color.
  for (node, color) in node_color.items():
    if color == "__CONFLICT__":
      node_color[node] = None


def update(adj_list, node_color, node):
  neighbors = adj_list[node]
  colored_neighbors = filter(None, [node_color[x] for x in neighbors])
  team_count = Counter(colored_neighbors)

  # If the node is colored, it gives itself a 3/2 vote.
  if node_color[node] is not None:
    team_count[node_color[node]] += 1.5

  most_common = team_count.most_common(1)
  if len(most_common) > 0 and \
    most_common[0][1] > len(colored_neighbors) / 2.0:
    return (True, most_common[0][0])

  return (False, node_color[node])


def is_stable(generation, max_rounds, prev, curr):
  if generation <= 1 or prev is None:
    return False

  # If we have reached the maximum number of generations, then stop.
  if generation == max_rounds:
    return True

  for node, color in curr.items():
    if not prev[node] == curr[node]:
      return False

  return True


def get_result(colors, node_color):
  color_nodes = {}
  for color in colors:
    color_nodes[color] = 0

  for node, color in node_color.items():
    if color is not None:
      color_nodes[color] += 1

  return color_nodes

if __name__ == '__main__':
  # Parse command-line arguments.
  parser = argparse.ArgumentParser(description='Get the graph and teams.')
  parser.add_argument("--graph")
  parser.add_argument("--files", nargs='+')
  args = parser.parse_args()
  (graph, files) = (args.graph, args.files)

  # Usage message.
  if graph is None or files is None:
    print "Usage: sim.py --graph [graph file name] --files " + \
      "[file(s) with nodes]"
    sys.exit(0)

  # Create the adjacency list for the graph and read nodes from file.
  adj_list = create_adj_list(graph)
  node_mappings = read_nodes(files)
  results = run_simulation(adj_list, node_mappings)
  print str(results)
