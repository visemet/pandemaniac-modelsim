from collections import Counter
from model import Model

class MostCommonColored(Model):
  """
  Class: MostCommonColored
  ------------------------
  A node takes on the color that is the most common among its neighbors..
  """

  def update(self, node_color, node):
    neighbors = self.adj_list[node]
    colored_neighbors = filter(None, [node_color[x] for x in neighbors])
    team_count = Counter(colored_neighbors)

    # If the node is colored, it gives itself a 3/2 vote.
    if node_color[node] is not None:
      team_count[node_color[node]] += 1.5

    # List of tuples of form (team, count). Make sure the most common color
    # appears strictly more times than the second most common color.
    most_commons = team_count.most_common(2)
    if len(most_commons) == 1 or \
      len(most_commons) >= 2 and most_commons[0][1] > most_commons[1][1]:
      return (True, most_commons[0][0])

    return (False, node_color[node])
