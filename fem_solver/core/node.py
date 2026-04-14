"""节点类 - 管理几何坐标和自由度"""

class Node:
    """有限元节点"""
    
    def __init__(self, id, x, y, z=None):
        """
        初始化节点
        
        参数:
        id: 节点编号
        x, y, z: 坐标（z可选，用于三维）
        """
        self.id = id
        self.x = float(x)
        self.y = float(y)
        self.z = float(z) if z is not None else None
        self.dofs = {}  # 自由度映射 {dof_type: dof_id}
        self.is_boundary = False  # 是否边界节点
        self.boundary_value = None  # 边界值
        
    def get_coordinates(self):
        """获取节点坐标"""
        if self.z is not None:
            return (self.x, self.y, self.z)
        return (self.x, self.y)
    
    def set_dof(self, dof_type, dof_id):
        """设置自由度"""
        self.dofs[dof_type] = dof_id
    
    def get_dof(self, dof_type):
        """获取自由度编号"""
        return self.dofs.get(dof_type)
    
    def __repr__(self):
        return f"Node({self.id}: ({self.x}, {self.y}))"