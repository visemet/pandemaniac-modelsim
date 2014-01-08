"""
Randomly matches teams with each other.
"""

import argparse
import random

def get_match(n, teams):
  matches = []

  random.shuffle(teams)
  for i in xrange(len(teams) / n + 1):
    if i * n == len(teams): break
    else:
      matches.append(" ".join(
        teams[i*n : ((i+1)*n if (i+1)*n <= len(teams) else len(teams))]))

  return matches


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  # Number of people per round.
  parser.add_argument("--n")
  parser.add_argument("--teams", nargs='+')
  args = parser.parse_args()
  (n, teams) = (int(args.n), args.teams)

  print str(get_match(n, teams))
