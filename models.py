"""
Class: models.py
----------------
Contains the different epidemic models.
"""

from collections import Counter
from copy import deepcopy
  
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


def next_majority_all(adj_list, node_team):
  """
  Function: next_majority_all
  ---------------------------
  Computes the next color for each node. The node takes on the color the
  majority of its neighbors have (including uncolored nodes).

  adj_list: The adjacency list.
  node_team: Mapping of nodes to their team.
  returns: A diff.
  """
  diff = {}
  node_team_copy = deepcopy(node_team)
  for node in adj_list:
    # Get the neighbors and find the team that covers the most neighbors.
    neighbors = adj_list[node]
    team_count = Counter([node_team[x] for x in neighbors])
    most_common = team_count.most_common(1)[0]

    # Convert if there is a majority team.
    if most_common[0] is not None and most_common[1] >= len(neighbors) / 2.0:
      new_color = most_common[0]
      diff[node] = new_color
      node_team_copy[node] = new_color

  return (node_team_copy, diff)


def next_majority_colored(adj_list, node_team):
  """
  Function: next_majority_colored
  -------------------------------
  Computes the next color for each node. The node takes on the color that
  the majority of its colored neighbors have.

  adj_list: The adjacency list.
  node_team: Mappin of nodes to their team.
  returns: A tuple containing the new nodes-to-team mapping and the diff.
  """
  diff = {}
  node_team_copy = deepcopy(node_team)
  for node in adj_list:
    # Get the neighbors and find the color that covers most neighbors.
    neighbors = adj_list[node]
    colored_neighbors = filter(None, [node_team[x] for x in neighbors])
    team_count = Counter(colored_neighbors)

    most_common = team_count.most_common(1)
    if len(most_common) > 0 and most_common[0][1] >= len(colored_neighbors) / 2.0:
      new_color = most_common[0][0]
      diff[node] = new_color
      node_team_copy[node] = new_color

  return (node_team_copy, diff)
