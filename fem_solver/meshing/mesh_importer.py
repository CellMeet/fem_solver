"""
网格导入器 - 将外部网格转换为求解器格式
"""

import numpy as np
import meshio


class MeshImporter:
    """
    网格导入器
    
    支持多种网格格式，转换为求解器可用的Mesh对象
    """
    
    def __init__(self):
        self.mesh_data = None
        self.physical_groups = {}
        
    def import_file(self, filename):
        """
        导入网格文件
        
        支持格式: .msh, .vtk, .vtu, .stl等
        
        参数:
            filename: 网格文件路径
        """
        print(f"导入网格: {filename}")
        
        try:
            self.mesh_data = meshio.read(filename)
        except Exception as e:
            raise RuntimeError(f"无法读取文件 {filename}: {e}")
        
        print(f"  节点数: {len(self.mesh_data.points)}")
        for cell_type, data in self.mesh_data.cells:
            print(f"  单元类型 {cell_type}: {len(data)} 个")
        
        # 提取物理组信息
        if hasattr(self.mesh_data, 'field_data'):
            self.physical_groups = self.mesh_data.field_data
        
        return self.mesh_data
    
    def convert_to_solver_mesh(self, mesh_data=None):
        """
        转换为求解器可用的Mesh对象
        
        返回:
            fem_solver.core.mesh.Mesh 对象
        """
        from fem_solver.core.mesh import Mesh
        from fem_solver.core.node import Node
        from fem_solver.core.element import TriangleElement
        
        if mesh_data is None:
            mesh_data = self.mesh_data
        
        if mesh_data is None:
            raise ValueError("没有导入的网格数据")
        
        solver_mesh = Mesh()
        
        # 创建节点
        for i, point in enumerate(mesh_data.points):
            node = Node(i, point[0], point[1], 
                        point[2] if len(point) > 2 else None)
            solver_mesh.nodes.append(node)
            solver_mesh.node_count += 1
        
        # 创建单元
        elem_id = 0
        for cell_type, cell_data in mesh_data.cells:
            for nodes_idx in cell_data:
                nodes = [solver_mesh.nodes[idx] for idx in nodes_idx]
                
                if cell_type == "triangle":
                    elem = TriangleElement(elem_id, nodes)
                    solver_mesh.elements.append(elem)
                    solver_mesh.element_count += 1
                    elem_id += 1
                elif cell_type == "tetra":
                    # 四面体单元（3D）
                    # 需要添加对应的单元类
                    pass
                # 可以添加更多单元类型
        
        print(f"转换完成: {solver_mesh.node_count} 节点, "
              f"{solver_mesh.element_count} 单元")
        
        return solver_mesh
    
    def get_physical_groups(self):
        """获取物理组信息"""
        return self.physical_groups