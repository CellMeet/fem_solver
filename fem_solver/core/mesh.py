# 这是必须的！不能删！
class Mesh:
    def __init__(self):
        self.nodes = []
        self.elements = []
        self.node_count = 0
        self.element_count = 0

class Node:
    def __init__(self, id, x, y, z=0.0):
        self.id = id
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
