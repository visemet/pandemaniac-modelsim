from collections import Counter
import json


def compute_next(node, adj_list, node_team):
  """
  compute_next
  ------------
  TODO
  """

  # Get the neighbors and find the team that covers the most neighbors.
  neighbors = adj_list[node]
  team_count = Counter([node_team[x] for x in neighbors])
  most_common = team_count.most_common(1)[0]

  # Don't convert if the team is None or there is no majority team. Return its
  # original team.
  if most_common[0] is None or most_common[1] < len(neighbors) / 2:
    return node_team[node]
  else:
    return most_common[0]


def run(team_nodes, adj_list):
  """
  run
  ---
  TODO

  team_nodes: The dictionary containing a mapping of a team name and the nodes
              they chose.
  adj_list: The adjacency list representation of the graph.
  """
  output = {}
  # Stores a mapping of nodes to their team.
  node_team = dict([(node, None) for node in adj_list])
  for (team, nodes) in team_nodes.items():
    print str((team, nodes))
    for node in nodes:
      # More than one team has chosen a node. TODO they cancel out
      if node_team[node] is not None:
        node_team[node] = "__CONFLICT__"
      else:
        node_team[node] = team
  for (node, team) in node_team.items():
    if team == "__CONFLICT__":
      node_team[node] = None
  output["0"] = to_team_mapping(node_team)

  generation = 1
  # Keep calculating the epidemic until it stops changing.
  while not is_stable(generation, output):
    for node in adj_list:
      # Compute the next team that this node has converted to.
      node_team[node] = compute_next(node, adj_list, node_team)

    # Convert the mapping of a node to the team into teams and their nodes.
    output[str(generation)] = to_team_mapping(node_team)
    generation += 1

  return json.dumps(output)


def is_stable(generation, output):
  """
  is_stable
  -----------
  Checks to see if the graph is still changing by comparing the current
  generation's colors with the previous generation's.

  generation: The current generation.
  output: The list of generations, teams, and their nodes.
  returns: True if the graph is stable, False otherwise.
  """

  # If this is the initial generation, nothing to check yet.
  if generation <= 1:
    return False

  current = output[str(generation - 1)]
  previous = output[str(generation - 2)]

  for team in current.keys():
    # If the two lists don't have the same elements.
    compare_lists = lambda x, y: Counter(x) == Counter(y)
    if not compare_lists(current[team], previous[team]):
      return False

  return True


def to_team_mapping(node_team):
  """
  to_team_mapping
  ---------------
  TODO
  """
  team_nodes = {}
  for node, team in node_team.items():
    if team in team_nodes:
      team_nodes[team].append(node)
    else:
      team_nodes[team] = [node]
  return team_nodes
