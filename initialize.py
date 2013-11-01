

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