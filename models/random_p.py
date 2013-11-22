from collections import Counter
from model import Model
import random

P = 0.2
SEED = 144144
random.seed(SEED)

class RandomP(Model):
  """
  Class: RandomP
  --------------
  Each neighbor of the node has a probability p of infecting the node. If more
  than one neighbor "infects" the node, then the node does not change its color.
  """

  def update(self, node_color, node):
    # Get the neighbors and their colors.
    neighbors = self.adj_list[node]
    neighbor_colors = filter(None, [node_color[x] for x in neighbors])

    (color_changed, current, original) = (False, None, node_color[node])
    # Go through each color.
    for color in neighbor_colors:
      should_infect = random.random() <= P
      # If this node has already been infected, then its color gets reset back
      # to the original color.
      if should_infect and color_changed:
        current = original
      # If this node has not been infected yet, can still change its color.
      elif should_infect:
        current = color
        color_changed = True

    # If the current color never changed, then this node did not change color.
    if current == original or current is None:
      return (False, current)
    else:
      return (True, current)
