from collections import Counter
from model import Model

class MajorityAll(Model):
  """
  Class: MajorityAll
  ------------------
  A node takes on the color that the majority of its neighbors have (including
  uncolored nodes).
  """

  def update(self, node_color, node):
    # Get the neighbors and find the team that covers the most neighbors.
    neighbors = self.adj_list[node]
    team_count = Counter([node_color[x] for x in neighbors])

    # If the node is colored, it gives itself a 3/2 vote.
    if node_color[node] is not None:
      team_count[node_color[node]] += 1.5

    most_common = team_count.most_common(1)[0]
    # Convert if there is a majority team.
    if most_common[0] is not None and most_common[1] > len(neighbors) / 2.0:
      return (True, most_common[0])

    return (False, node_color[node])
