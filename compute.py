import argparse
from collections import Counter
import json
import operator
from Queue import Queue
import random

MAX_DIST = 293879873

def floyd_warshall(adj_list):
  """
  Function: floyd_warshall
  ------------------------
  Finds the shortest path between all nodes using the Floyd-Warshall
  algorithm.
  """
  # Initialize the dictionary of distances.
  init_dict = dict([(node, MAX_DIST) for node in adj_list.keys()])
  dist = dict([(node, init_dict) for node in adj_list.keys()])
  nodes = dist.keys()
  for i in nodes:
    for j in nodes:
      # If finding distance between the same vertex, the distance is 0.
      if i == j:
        dist[i][j] = 0
      # If there is an edge, the distance is 1.
      elif j in adj_list[i]:
        dist[i][j] = 1

  # Update distances.
  for i in nodes:
    print "."
    for j in nodes:
      for k in nodes:
        new_dist = dist[j][i] + dist[i][k]
        if new_dist < dist[j][k]:
          dist[j][k] = new_dist
  return dist


def shortest_path(adj_list):
  """
  Function: shortest_path
  -----------------------
  Finds the shortest path between all nodes using a breadth-first search
  from each node.
  """
  init_dict = dict([(node, MAX_DIST) for node in adj_list.keys()])
  dist = dict([(node, init_dict) for node in adj_list.keys()])
  nodes = dist.keys()
  # Do the breadth-first search from each node.
  for node in nodes:
    queue = Queue()
    s = set()
    s.add(node)
    for neighbor in adj_list[node]:
      if neighbor not in s:
        queue.put(neighbor)
        s.add(neighbor)
      dist[node][neighbor] = 1

    while not queue.empty():
      curr = queue.get()
      curr_dist = dist[node][curr]
      neighbors = adj_list[curr]
      for neighbor in neighbors:
        dist[node][neighbor] = curr_dist + 1
        if neighbor not in s:
          queue.put(neighbor)
          s.add(neighbor)


def by_degree(adj_list, num):
  """
  Function: by_degree
  -------------------
  Finds the top num nodes with the highest degree.
  """
  degrees = dict([(k, len(v)) for (k, v) in adj_list.items()])
  degrees = sorted(degrees.iteritems(), key=operator.itemgetter(1), \
    reverse=True)

  top_degrees = [x[0] for x in degrees][0:num]
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
  dist = shortest_path(adj_list)
  # List of tuples of the form (closeness, node).
  closeness = [(sum([l for l in dist[node] if l != MAX_DIST]), node) \
    for node in dist.keys()]
  closeness = sorted(closeness, key=lambda tup: tup[0])
  return closeness[0:num]


def by_betweenness(adj_list, num):
  pass
  
  


def by_random(adj_list, num):
  """
  Function: by_random
  -------------------
  Selects num random nodes.
  """
  return random.sample(adj_list.keys(), num)


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
    result = by_degrees(adj_list, num)
  elif method == "closeness":
    result = by_centrality(adj_list, num)
  elif method == "betweeness" or method == "betweenness":
    result = by_beteweenness(adj_list, num)
  else:#if method == "random":
    result = by_random(adj_list, num)

  output = open("nodes.txt", "w")
  for elem in result:
    output.write(str(elem) + "\n")
  output.close()
