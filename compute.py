import argparse
import json
import networkx as nx
import random

def by_clustering(adj_list, num):
  """
  Function: by_clustering
  -----------------------
  Finds the top num nodes with the highest clustering.
  """

  def get_triangles(node):
    """
    Function: get_triangles
    -----------------------
    Gets the number of triangles centered at this node.
    """
    triangles = 0
    neighbors = adj_list[node]
    for n1 in neighbors:
      for n2 in neighbors:
        if n2 in adj_list[n1]:
          triangles += 1
    return triangles

  def get_triples(node):
    """
    Function: get_triples
    ---------------------
    Returns the number of triples centered at this node.
    """
    degree = len(adj_list[node])
    return degree * (degree - 1) / 2


  cluster = []
  for node in adj_list.keys():
    clustering = 0
    # Clustering defined to be 0 if there were no triples.
    if get_triples(node) != 0:
      clustering = get_triangles(node) / get_triples(node)
    cluster.append((clustering, node))

  cluster = sorted(cluster, key=lambda tup: tup[0], reverse=True)
  return [x[1] for x in cluster[0:num]]


def by_random(adj_list, num):
  """
  Function: by_random
  -------------------
  Selects num random nodes.
  """
  return random.sample(adj_list.keys(), num)


def create_graph(adj_list):
  """
  Function: create_graph
  ----------------------
  Creates a NetworkX graph from an adjacency list.
  """
  G = nx.Graph()
  # Loop through the adjacency list to add edges.
  for (n1, neighbors) in adj_list.items():
    for n2 in neighbors:
      G.add_edge(n1, n2)
      G.add_edge(n2, n1)
  return G


def get_top_N(adj_list, method, num):
  """
  Function: get_top_N
  -------------------
  Get the top N nodes of the graph using a particular method.

  adj_list: Adjacency representation of the graph.
  method: The method used to compute the "value" of each node.
  num: The number of nodes to take.
  """
  G = create_graph(adj_list)
  results = {}
  if method == "degree":
    results = nx.degree_centrality(G)
  elif method == "closeness":
    results = nx.closeness_centrality(G)
  elif method == "betweeness" or method == "betweenness":
    results = nx.betweenness_centrality(G)
  elif method == "clustering":
    return by_cluster(adj_list, num)
  elif method == "random":
    return by_random(adj_list, num)

  # Get the top N.
  results = sorted(results.items(), key=lambda x: x[1], reverse=True)
  return [x[0] for x in results[0:num]]


if __name__ == "__main__":
  # Parse the command-line arguments to get the graph and teams participating.
  parser = argparse.ArgumentParser(description='Get the graph and teams.')
  parser.add_argument("--graph")
  parser.add_argument("--num")
  parser.add_argument("--method")
  args = parser.parse_args()
  (graph, num, method) = (args.graph, int(args.num), args.method)

  graph_file = open("private/graphs/" + graph + ".txt", "r")
  adj_list = json.loads("".join(graph_file.readlines()))
  graph_file.close()

  nodes = get_top_N(adj_list, method, num)
  output = open(graph + "-" + method + "-" + str(num) + ".txt", "w")
  for node in nodes:
    output.write(str(node) + "\n")
  output.close()
  