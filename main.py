import argparse
import simulation

def create_adj_list(graph):  
  """
  create_adj_list
  ---------------
  Creates the adjacency list representation of the graph from a file containing
  the graph.

  graph: The graph to create an adjacency list for.
  returns: An adjacency list.
  """
  adj_list = {}
  graph_file = open("google.txt", "r")

  for line in graph_file:
    from_node = line.split()[0]
    to_node = line.split()[1]

    if from_node not in adj_list:
      adj_list[from_node] = [to_node]
    else:
      adj_list[from_node].append(to_node)
  return adj_list


def read_nodes(graph, teams):
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
  node_list = {}
  for team in teams:
    team_file = open("TODO", "r")


if __name__ == "__main__":
  # Parse the command-line arguments to get the graph and teams participating.
  parser = argparse.ArgumentParser(description='Get the graph and teams.')
  parser.add_argument("-graph")
  parser.add_argument("-teams", nargs='+')
  args = parser.parse_args()
  (graph, teams) = (args.graph, args.teams)

  # Create the adjacency list for the graph.
  adj_list = create_adj_list(graph)

  # Read in the node selection for each team.
  node_list = read_nodes(graph, teams)

  # Run the simulation.
  simulation.run(node_list, adj_list)
