"""网格管理"""

from .node import Node
from .element import TriangleElement

class Mesh:
    """有限元网格"""
    
    def __init__(self):
        self.nodes = []      # 节点列表
        self.elements = []   # 单元列表
        self.node_count = 0
        self.element_count = 0
        
    def create_rectangular_mesh(self, xmin, xmax, ymin, ymax, nx, ny):
        """
        创建矩形区域的三角形网格
        
        参数:
        xmin, xmax: x范围
        ymin, ymax: y范围
        nx, ny: x和y方向的分割数
        """
        dx = (xmax - xmin) / nx
        dy = (ymax - ymin) / ny
        
        # 创建节点
        node_grid = []
        for i in range(nx + 1):
            x = xmin + i * dx
            row = []
            for j in range(ny + 1):
                y = ymin + j * dy
                node = Node(self.node_count, x, y)
                self.nodes.append(node)
                row.append(node.id)
                self.node_count += 1
            node_grid.append(row)
        
        # 创建单元
        for i in range(nx):
            for j in range(ny):
                n1 = node_grid[i][j]
                n2 = node_grid[i+1][j]
                n3 = node_grid[i+1][j+1]
                n4 = node_grid[i][j+1]
                
                # 第一个三角形
                nodes1 = [self.nodes[n1], self.nodes[n2], self.nodes[n3]]
                elem1 = TriangleElement(self.element_count, nodes1)
                self.elements.append(elem1)
                self.element_count += 1
                
                # 第二个三角形
                nodes2 = [self.nodes[n1], self.nodes[n3], self.nodes[n4]]
                elem2 = TriangleElement(self.element_count, nodes2)
                self.elements.append(elem2)
                self.element_count += 1
        
        return node_grid
    
    def get_boundary_nodes(self, boundary_func):
        """
        获取边界节点
        
        参数:
        boundary_func: 判断是否为边界的函数
        """
        boundary_nodes = []
        for node in self.nodes:
            if boundary_func(node.x, node.y):
                node.is_boundary = True
                boundary_nodes.append(node)
        return boundary_nodes
    
    def __repr__(self):
        return f"Mesh(nodes={self.node_count}, elements={self.element_count})"