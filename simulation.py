from collections import Counter, OrderedDict

def compute_next(node, adj_list, node_team):
  """
  compute_next
  ------------
  Computes the next team for the node, depending on the epidemic mode.

  node: The node to compute the next team.
  adj_list: The adjacency list representation of the graph.
  node_team: The mapping of nodes to their team.

  returns: A tuple containing (team, team_changed) where team is the new team
           of this node, and is_changed is set to True if the team changed.
  """

  # Get the neighbors and find the team that covers the most neighbors.
  neighbors = adj_list[node]
  team_count = Counter([node_team[x] for x in neighbors])
  most_common = team_count.most_common(1)[0]

  # Don't convert if the team is None or there is no majority team. Return its
  # original team.
  
  # TODO? if no team is majority, don't spread?
  
  if most_common[0] is None or most_common[1] < len(neighbors) / 2:
    return (node_team[node], False)
  else:
    return (most_common[0], True)


def run(team_nodes, adj_list):
  """
  run
  ---
  Runs the epidemic simulation for each cycle of the epidemic until it stops
  changing.

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
  # The current diff being generated. Contains only new mappings of nodes to
  # their teams.
  diff = {}

  # Initially set the node to the team that chooses it. If more than one team
  # chooses the same node, then no team gets that node.
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

  # Initial generation.
  output["0"] = to_team_mapping(diff)
  generation = 1

  # Keep calculating the epidemic until it stops changing.
  while not is_stable(generation, output):
    diff = {}
    for node in adj_list:
      # Compute the next team that this node has converted to.
      (node_team[node], team_changed) = compute_next(node, adj_list, node_team)
      if team_changed:
        diff[node] = node_team[node]

    # Convert the mapping of a node to the team into teams and their nodes.
    output[str(generation)] = to_team_mapping(diff)
    generation += 1

  return (output, to_team_mapping(node_team))


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


def to_team_mapping(diff):
  """
  to_team_mapping
  ---------------
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
