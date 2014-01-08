from match import get_match
from main import do_main

import argparse

DAYS = {
  "1": [
    # ([graph name], [number of players]) OR
    # ([graph name], [team name]) which means it's a 1 vs. 1 with a specific
    #                             TA team and a student team.
    ("2.5.x", 2),
    ("4.5.x", 4),
    ("4.10.x", 4),
    ("8.10.x", 8),
    ("8.20.x", 8),
    ("8.x.x", 8),
    ("8.x.x", 8),
    ("2.10.x", "TA-degree"),
    ("2.10.x", "TA-fewer"),
    ("2.10.x", "TA-eyeball")
  ],
}

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  # Day of the practice rounds or competition.
  parser.add_argument("--day")
  parser.add_argument("--teams", nargs="+")
  args = parser.parse_args()
  (day, teams) = (args.day, args.teams)

  config = DAYS[day]
  # Loop through each graph for this day/competition round.
  for (graph, num_teams) in config:
    # If this is a one-on-one with a TA team.
    if type(num_teams) == str:
      ta_team = num_teams
      for team in teams: 
        do_main(graph, [team, ta_team], "majority_colored")

    # Otherwise match just the student teams.
    else:
      matches = get_match(num_teams, teams)
      for match in matches:
        do_main(graph, match, "majority_colored")
