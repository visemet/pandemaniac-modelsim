import argparse
import json
import networkx as nx
import os
import random

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
      G.add_edge(str(n1), str(n2))
      G.add_edge(str(n2), str(n1))
  return G


def randomize(lst1, lst2):
  """
  Function: randomize
  -------------------
  Combines two lists and shuffles them as if we were randomly picking nodes
  from each one of them.
  """
  result = lst1 + lst2
  random.shuffle(result)
  return result


def sort(nodes):
  """
  Function: sort
  --------------
  Sorts a list of nodes by the second element in the tuple.
  """
  nodes = sorted(list(set(nodes.items())), key=lambda x: x[1], reverse=True)
  return [x[0] for x in nodes]


def subset(adj_list, nodes):
  """
  Function: subset
  ----------------
  Gets a subset of an adjacency list with particular nodes.
  """
  return dict([x for x in adj_list.items() if x[0] in nodes])


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
    for i in xrange(len(neighbors)):
      for j in xrange(i + 1, len(neighbors)):
        if neighbors[j] in adj_list[str(neighbors[i])]:
          triangles += 1
    return triangles

  def get_triples(node):
    """
    Function: get_triples
    ---------------------
    Returns the number of triples centered at this node.
    """
    degree = len(adj_list[node])
    return degree * (degree - 1) / 2.0


  cluster = {}
  for node in adj_list.keys():
    clustering = 0
    # Clustering defined to be 0 if there were no triples.
    if get_triples(node) != 0:
      clustering = get_triangles(node) / get_triples(node)
    cluster[node] = clustering

  return cluster


def by_random(adj_list, num):
  """
  Function: by_random
  -------------------
  Selects num random nodes.
  """
  return random.sample(adj_list.keys(), num)


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
    results = sort(nx.degree_centrality(G))
  elif method == "closeness":
    results = sort(nx.closeness_centrality(G))
  elif method == "betweeness" or method == "betweenness":
    results = sort(nx.betweenness_centrality(G))
  elif method == "clustering":
    results = sort(by_clustering(adj_list, num))
  elif method == "degree-clustering":
    r1 = sort(nx.degree_centrality(G))
    r2 = sort(by_clustering(adj_list, num))
    results = randomize(r1[0:num], r2[0:num])
  elif method == "b-clustering":
    c = sort(by_clustering(adj_list, num))
    G = create_graph(subset(adj_list, c[0:num*4]))
    results = sort(nx.betweenness_centrality(G))
  elif method.startswith("random"):
    return by_random(adj_list, num)

  # Get the top N.
  return results[0:num]


def main(graph, num, method):
  graph_file = open("private/graphs/" + graph, "r")
  adj_list = json.loads("".join(graph_file.readlines()))
  graph_file.close()

  nodes = get_top_N(adj_list, method, num)
  path = "private/uploads/" + method
  if not os.path.exists(path):
    os.makedirs(path)
  output = open(path + "/" + graph + "-" + str(num), "w")
  for node in nodes:
    output.write(str(node) + "\n")
  output.close()


if __name__ == "__main__":
  # Parse the command-line arguments to get the graph and teams participating.
  parser = argparse.ArgumentParser(description='Get the graph and teams.')
  parser.add_argument("--graph")
  parser.add_argument("--num")
  parser.add_argument("--method")
  args = parser.parse_args()
  (graph, num, method) = (args.graph, int(args.num), args.method)
  main(graph, num, method)
