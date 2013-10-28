import argparse
from collections import Counter
import json
import operator
import random

def by_degrees(adj_list, num):
  degrees = dict([(k, len(v)) for (k, v) in adj_list.items()])
  degrees = sorted(degrees.iteritems(), key=operator.itemgetter(1), reverse=True)

  top_degrees = [x[0] for x in degrees][0:num]
  return top_degrees


def by_random(adj_list, num):
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
  if method == "degrees":
    result = by_degrees(adj_list, num)
  if method == "random":
    result = by_random(adj_list, num)

  output = open("nodes.txt", "w")
  for elem in result:
    output.write(str(elem) + "\n")
  output.close()
