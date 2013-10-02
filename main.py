import argparse
import json
import simulation

def create_adj_list(graph):  
  """
  create_adj_list
  ---------------
  Creates the adjacency list representation of the graph from a file containing
  the graph. The file is in JSON format.

  graph: The graph to create an adjacency list for.
  returns: An adjacency list.
  """
  graph_file = open("TODOadjlist.txt", "r")
  adj_list = json.loads("".join(graph_file.readlines()))
  graph_file.close()
  return adj_list


def read_nodes(graph, valid_nodes, teams):
  """
  read_nodes
  ----------
  Reads in the node selection for a team and creates a mapping of the team to
  the nodes they chose.

  graph: The corresponding graph.
  teams: The list of teams.
  returns: A dictionary containing the key as the team and the value as the
           list of chosen nodes.
  """
  team_nodes = {}
  for team in teams:
    team_file = open("TODOteam.txt", "r") # TODO file should have graph and team
    # Read in all of the nodes and filter out spaces and newlines.
    nodes = filter(lambda x: x.strip(), team_file.read().split("\n"))
    team_file.close()

    # If the team submits an invalid list of nodes (i.e. nodes that do not
    # exist, then their entire submission is invalidated TODO.
    is_valid = reduce(lambda x, node: x and (node in valid_nodes), nodes)
    if is_valid:
      team_nodes[team] = nodes
    else:
      team_nodes[team] = []

  return team_nodes


if __name__ == "__main__":
  # Parse the command-line arguments to get the graph and teams participating.
  parser = argparse.ArgumentParser(description='Get the graph and teams.')
  parser.add_argument("--graph")
  parser.add_argument("--teams", nargs='+')
  args = parser.parse_args()
  (graph, teams) = (args.graph, args.teams)

  # Create the adjacency list for the graph.
  adj_list = create_adj_list(graph)

  # Read in the node selection for each team.
  team_nodes = read_nodes(graph, adj_list.keys(), teams)

  # Run the simulation.
  output = simulation.run(team_nodes, adj_list)
  
  print str(output)
