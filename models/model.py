class Model:
  """
  Class: Model
  ------------
  An epidemic model. To be implemented for specific models.
  """

  def __init__(self, adj_list):
    # The adjacency list for the graph.
    self.adj_list = adj_list


  def update(self, node_color, node):
    """
    Function: update
    ----------------
    Update the node with its new color, given the current mappings of nodes
    to their colors.

    node_color: A dictionary containing a mapping of the nodes to their color.
    node: The node to update the color of.
    """
    pass
