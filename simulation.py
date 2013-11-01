from collections import Counter, OrderedDict
from copy import deepcopy

class Simulation:
  """
  Class: Simulation
  -----------------
  Simulates the epidemic using different epidemic models.
  """

  def __init__(self, max_rounds, model, team_nodes, adj_list):
    # The maximum number of rounds to run the simulation.
    self.max_rounds = max_rounds
    # A mapping of the teams and the nodes they chose.
    self.team_nodes = team_nodes
    # The adjacency list of the graph.
    self.adj_list = adj_list

    # Import the correct module for the model.
    if model == "majority_all":
      from models.majority_all import MajorityAll
      self.model = MajorityAll(self.adj_list)
    elif model == "majority_colored":
      from models.majority_colored import MajorityColored
      self.model = MajorityColored(self.adj_list)
    elif model == "weighted_random":
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
             results is the final mapping of teams to their nodes.
    """
    # Stores a mapping of nodes to their team.
    node_team = dict([(node, None) for node in self.adj_list])
    # Output to be written to file.
    output = OrderedDict()

    # Choose the initial colors for the nodes based on the teams' selections.
    diff = init_conflict(self.team_nodes, node_team)
    output["0"] = to_team_mapping(diff)
    generation = 1

    # Keep calculating the epidemic until it stops changing.
    while not is_stable(generation, self.max_rounds, output):
      print "Generation:", str(generation)
      diff = {}
      node_team_copy = deepcopy(node_team)
      # Find the new color for every node. The model can be changed.
      for node in self.adj_list:
        (changed, color) = self.model.update(node_team, node)
        # Store the node's new color only if it changed.
        if changed:
          diff[node] = color
          node_team_copy[node] = color
      node_team = node_team_copy

      # Convert the mapping of a node to the team into teams and their nodes.
      output[str(generation)] = to_team_mapping(diff)
      generation += 1

    return (output, to_team_mapping(node_team))


def init_conflict(team_nodes, node_team):
  """
  Function: init_conflict
  -----------------------
  Initializes nodes for the teams. If two teams choose the same node then no
  team gets that node.

  team_nodes: A mapping of a team name to the nodes they chose.
  node_team: Mapping of nodes to their team.
  returns: An initial diff.
  """
  diff = {}

  for (team, nodes) in team_nodes.items():
    for node in nodes:
      # More than one team has chosen a node. They cancel out.
      if node_team[node] is not None:
        node_team[node] = "__CONFLICT__"
        diff[node] = "__CONFLICT__"
      else:
        node_team[node] = team
        diff[node] = team
  # Now set all the conflicts back to None since no team gets those nodes.
  for (node, team) in node_team.items():
    if team == "__CONFLICT__":
      node_team[node] = None

  return diff


def is_stable(generation, max_rounds, output):
  """
  Function: is_stable
  -------------------
  Checks to see if the graph is still changing by comparing the current
  generation's node-to-team mappings with the previous generation's.

  generation: The current generation.
  max_rounds: The maximum number of generations to run for.
  output: The list of generations, teams, and their nodes.
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
