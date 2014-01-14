from collections import Counter, OrderedDict
from copy import deepcopy
from random import shuffle, randint

class Simulation:
  """
  Class: Simulation
  -----------------
  Simulates the epidemic using different epidemic models.
  """

  def __init__(self, model, color_nodes, adj_list):
    # The maximum number of rounds to run the simulation. Randomly chosen
    # number between 100 and 200.
    self.max_rounds = randint(100, 200)
    # A mapping of the colors and the nodes of that color.
    self.color_nodes = color_nodes
    # The adjacency list of the graph.
    self.adj_list = adj_list

    # Import the correct module for the model.
    if model == "majority_all":
      from models.majority_all import MajorityAll
      self.model = MajorityAll(self.adj_list)
    elif model == "majority_colored":
      from models.majority_colored import MajorityColored
      self.model = MajorityColored(self.adj_list)
    elif model == "most_common_colored":
      from models.most_common_colored import MostCommonColored
      self.model = MostCommonColored(self.adj_list)
    elif model == "random_p":
      from models.random_p import RandomP
      self.model = RandomP(self.adj_list)
    elif model == "weighted_random":
      from models.weighted_random import WeightedRandom
      self.model = WeightedRandom(self.adj_list)
    else:
      print "Not a valid model. Random model selected."
      from models.weighted_random import WeightedRandom
      self.model = WeightedRandom(self.adj_list)


  def run(self):
    """
    Function: run
    -------------
    Runs the epidemic simulation for each generation of the epidemic until there
    is no more change (i.e. it is stable) or we reach the maximum number of
    generations.

    returns: A tuple (output, results) where the output is a dictionary object
             containing a mapping of each generation to the diff generated and
             results is the final mapping of colors to their nodes.
    """
    # Stores a mapping of nodes to their color.
    node_color = dict([(node, None) for node in self.adj_list])
    # Output to be written to file.
    output = OrderedDict()

    # Choose the initial colors for the nodes.
    diff = init(self.color_nodes, node_color)
    color_mappings = to_color_mapping(diff)

    # Make sure all colors are in the initial diff.
    for color in self.color_nodes.keys():
      if color not in color_mappings:
        color_mappings[color] = []
    output["0"] = color_mappings
    generation = 1

    # Keep calculating the epidemic until it stops changing.
    nodes = self.adj_list.keys()
    while not is_stable(generation, self.max_rounds, output):
      print ".",
      diff = {}
      # Get the next color for the nodes.
      node_color_copy = deepcopy(node_color)
      for node in nodes:
        (changed, color) = self.model.update(node_color, node)
        # Store the node's new color only if it changed.
        if changed:
          diff[node] = color
          node_color_copy[node] = color
      node_color = node_color_copy

      # Convert the mapping of a node to its color into colors and
      # corresponding nodes.
      output[str(generation)] = to_color_mapping(diff)
      generation += 1

    print "\nTotal:", generation, "generations."
    return (output, final_color_mapping(self.color_nodes.keys(), node_color))


def init(color_nodes, node_color):
  """
  Function: init
  --------------
  Initializes nodes for each color. If more than one color is selected for a
  node, then that node does not any of the colors.

  color_nodes: A mapping of a color to the nodes of that color..
  node_color: Mapping of nodes to their color.
  returns: An initial diff.
  """
  diff = {}
  for (color, nodes) in color_nodes.items():
    for node in nodes:
      # More than one color has been selected for a node. They cancel out.
      if node_color[node] is not None:
        node_color[node] = "__CONFLICT__"
        diff[node] = "__CONFLICT__"
      else:
        node_color[node] = color
        diff[node] = color
  # Now set all the conflicts back to None since those nodes don't get any
  # color.
  for (node, color) in node_color.items():
    if color == "__CONFLICT__":
      node_color[node] = None

  return diff


def is_stable(generation, max_rounds, output):
  """
  Function: is_stable
  -------------------
  Checks to see if the graph is still changing by comparing the current
  generation's node-to-color mappings with the previous generation's.

  generation: The current generation.
  max_rounds: The maximum number of generations to run for.
  output: The list of generations, colors, and nodes of that color.
  returns: True if the graph is stable, False otherwise.
  """

  # If this is the initial generation, nothing to check yet.
  if generation <= 1:
    return False

  # If we have reached the maximum number of generations, then stop.
  if generation == max_rounds:
    return True

  current = output[str(generation - 1)]
  previous = output[str(generation - 2)]

  for color in current.keys():
    # If the two lists don't have the same elements.
    compare_lists = lambda x, y: Counter(x) == Counter(y)
    if not compare_lists(current[color], previous[color]):
      return False

  return True


def to_color_mapping(diff):
  """
  Function: to_color_mapping
  --------------------------
  Converts a dictionary from node -> color to color -> nodes.

  diff: The dictionary to convert.
  returns: A new dictionary containing a mapping of colors to nodes of that
           color.
  """
  color_nodes = {}
  for node, color in diff.items():
    # Ignore conflicts.
    if color == "__CONFLICT__":
      continue
    if color in color_nodes:
      color_nodes[color].append(node)
    else:
      color_nodes[color] = [node]
  return color_nodes


def final_color_mapping(colors, node_color):
  """
  Function: final_color_mapping
  -----------------------------
  Computes the final mappings from colors to the nodes of that color.

  colors: The list of colors.
  node_color: A mapping from nodes to their color.
  """
  color_nodes = {}
  for color in colors:
    color_nodes[color] = []

  for node, color in node_color.items():
    if color is not None:
      color_nodes[color].append(node)

  return color_nodes
