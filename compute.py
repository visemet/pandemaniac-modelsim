import argparse
from collections import Counter
import json
from multiprocessing import Process
import operator
from Queue import Queue
import random

from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import floyd_warshall as fw
import numpy as np

MAX_DIST = 293879873

# ----------------------------- Computation Methods ---------------------------

def by_degree(adj_list, num):
  """
  Function: by_degree
  -------------------
  Finds the top num nodes with the highest degree.
  """
  degrees = [(len(v), k) for (k, v) in adj_list.items()]
  degrees = sorted(degrees, key=lambda tup: tup[0], reverse=True)

  top_degrees = [x[1] for x in degrees[0:num]]
  return top_degrees


def by_closeness(adj_list, num):
  """
  Function: by_closeness
  ----------------------
  Finds the top num nodes with the highest closeness centrality. This is
  defined as the reciprocal of the average distance between the node and all
  other nodes.

  Closeness(i) = (n - 1) / Sum_(j != i) l(i, j)
  Where l(i, j) is the length of the shortest path between nodes i and j.
  """
  # Need to re-index the adjacency list.
  (adj_list, node_mappings) = reindex(adj_list)
  (dist, _) = shortest_path(adj_list)

  # List of tuples of the form (closeness, node).
  closeness = [(sum([l for l in dist[node] if l < MAX_DIST]), node) \
    for node in range(len(dist))]
  closeness = sorted(closeness, key=lambda tup: tup[0], reverse=True)

  return unindex([x[1] for x in closeness[0:num]], node_mappings)


def by_betweenness(adj_list, num):
  """
  Function: by_betweenness
  ------------------------
  Finds the top num nodes with the highest betweenness centrality. We let
  P(j, k) denote the number of shortest paths between nodes j and k, and
  P_i (j, k) be the number of those shortest paths that pass through i.

  Betweenness is then:
    Sum_(j != k != i) P_i (j, k) / P(j, k)
    --------------------------------------
             ((n - 1) choose 2)
  """
  # Need to re-index the adjacency list.
  (adj_list, node_mappings) = reindex(adj_list)
  (dist, pred) = floyd_warshall(adj_list)

  # Predecessors is structured as an N x N matrix. The ith row represents
  # shortest paths from point i. Each entry (i, j) represents the index
  # of the previous node in the shortest path from i to j.

  # Array to store the number of shortest paths from j to k. The entry
  # (j, k) is the number of shortest paths from j to k.
  P_jk = [[0] * len(adj_list)] * len(adj_list)
  # Array to store the number of shortest paths that pass through i.
  P_i = [0] * len(adj_list)

  between = []
  # TODO: This does not work, because it is too slow in Python. Please refer
  # to the Java version.
  between = sorted(between, key=lambda tup: tup[0], reverse=True)
  return unindex([x[1] for x in between[0:num]], node_mappings)
  pass


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
        if neighbors[j] in adj_list[neighbors[i]]:
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


# ------------------------------- Helper Methods ------------------------------

def reindex(adj_list):
  """
  Function: reindex
  -----------------
  Re-indexes a graph's nodes so they are numbered from 0 to (N - 1) where
  N is the number of nodes.

  returns: A tuple (new_adj_list, node_mappings) where new_adj_list is the
           new adjacency list with the new node mappings, and node_mappings
           is a map that can convert the new numbering back to the old
           numbering.
  """
  new_adj_list = {}
  node_mappings = {}
  i = 0
  for node in adj_list.keys():
    if node not in node_mappings:
      node_mappings[node] = i
      i += 1
    new_node = node_mappings[node]
    new_adj_list[new_node] = []
    for neighbor in adj_list[node]:
      if neighbor not in node_mappings:
        node_mappings[neighbor] = i
        i += 1
      new_adj_list[new_node].append(node_mappings[neighbor])

  # Reverse the node mappings to be able to un-index later.
  node_mappings = dict([(new, old) for (old, new) in node_mappings.iteritems()])
  return (new_adj_list, node_mappings)


def unindex(lst, node_mappings):
  """
  Function: unindex
  -----------------
  Maps the new node mappings back to the old one.

  lst: The list to remap.
  node_mappings: The node mappings.

  returns: The list with the new mappings.
  """
  return [node_mappings[x] for x in lst]


def floyd_warshall(adj_list):
  """
  Function: floyd_warshall
  ------------------------
  Finds the shortest path between all nodes using the Floyd-Warshall
  algorithm. WARNING! This is very slow.
  """
  N = len(adj_list)

  # Initialize the dictionary of distances (which is an N x N matrix).
  dist = [[MAX_DIST] * N] * N
  for i in xrange(N):
    # Distance between vertex to itself is 0.
    dist[i][i] = 0
    # If there is an edge, the distance is 1.
    for j in adj_list[i]:
        dist[i][j] = 1

  # Update distances.
  for i in xrange(N):
    for j in xrange(N):
      for k in xrange(N):
        new_dist = dist[j][i] + dist[i][k]
        if new_dist < dist[j][k]:
          dist[j][k] = new_dist
  return (dist, [])


def shortest_path(adj_list):
  """
  Function: shortest_path
  -----------------------
  Finds the all-pairs shortest path using the SciPy library in conjuction with
  NumPy.

  returns: A tuple containing the (distances, predecessor matrix) where
           predecessor matrix contains information on the actual shortest path
           between nodes.
  """
  n = len(adj_list)
  matrix = np.zeros((n, n), dtype=np.int)
  for n1 in adj_list.keys():
    for n2 in adj_list[n1]:
      matrix[n1][n2] = 1
  (dists, preds) = fw(csr_matrix(matrix), directed=False, unweighted=True, \
    return_predecessors=True)
  return (dists.tolist(), preds.tolist())


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

  result = []
  if method == "degree":
    result = by_degree(adj_list, num)
  elif method == "closeness":
    result = by_closeness(adj_list, num)
  elif method == "betweeness" or method == "betweenness":
    result = by_betweenness(adj_list, num)
  elif method == "clustering":
    result = by_clustering(adj_list, num)
  elif method == "random":
    result = by_random(adj_list, num)

  output = open("nodes.txt", "w")
  for elem in result:
    output.write(str(elem) + "\n")
  output.close()
