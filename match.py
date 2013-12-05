"""
Randomly matches teams with each other.
"""

import argparse
import random

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  # Number of people per round.
  parser.add_argument("--n")
  parser.add_argument("--teams", nargs='+')
  args = parser.parse_args()
  (n, teams) = (int(args.n), args.teams)

  random.shuffle(teams)
  print ""
  for i in xrange(len(teams) / n + 1):
    if i*n == len(teams): break
    else:
      print " ".join(teams[i*n : ((i+1)*n if (i+1)*n <= len(teams) else len(teams))])
