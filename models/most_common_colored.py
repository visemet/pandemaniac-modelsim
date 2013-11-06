from collections import Counter
from model import Model

class MostCommonColored(Model):
  """
  Class: MostCommonColored
  ------------------------
  A node takes on the color that is the most common among its neighbors..
  """

  def update(self, node_team, node):
    neighbors = self.adj_list[node]
    colored_neighbors = filter(None, [node_team[x] for x in neighbors])
    team_count = Counter(colored_neighbors)

    most_common = team_count.most_common(1)
    if len(most_common) > 0:
      return (True, most_common[0][0])

    return (False, node_team[node])
