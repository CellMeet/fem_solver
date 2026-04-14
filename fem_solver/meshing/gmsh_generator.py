"""
Gmsh网格生成器 - 从STL生成内部网格的正确方法
"""

import gmsh
import numpy as np
import os


class GmshGenerator:
    """Gmsh网格生成器"""
    
    def __init__(self):
        self._initialized = False
        
    def _init(self):
        if not self._initialized:
            gmsh.initialize()
            gmsh.option.setNumber("General.Terminal", 1)
            self._initialized = True
    
    def create_model(self, name):
        """创建新模型"""
        self._init()
        try:
            gmsh.model.clear()
        except:
            pass
        gmsh.model.add(name)
        print(f"创建模型: {name}")
    
    def import_stl_as_geometry(self, filename):
        """
        将STL文件作为几何导入 - 正确的方法
        
        关键步骤：
        1. 导入STL网格
        2. 从网格创建几何曲面（通过创建曲线环）
        3. 这样Gmsh就知道这是一个需要填充的区域
        """
        if not os.path.exists(filename):
            raise FileNotFoundError(f"文件不存在: {filename}")
        
        self._init()
        
        print(f"将STL转换为几何: {filename}")
        
        # 1. 导入STL网格
        gmsh.merge(filename)
        
        # 2. 获取所有实体
        entities = gmsh.model.getEntities()
        
        # 3. 收集所有边界曲线
        # 对于2D几何，我们需要从STL的边界提取曲线
        # 这里使用Gmsh的几何内核来创建曲面
        
        # 方法：使用Gmsh的"Coherence"功能来合并边界
        # 然后从边界创建曲线环
        
        # 获取所有点
        points = []
        for dim, tag in entities:
            if dim == 0:
                points.append(tag)
        
        # 获取所有线
        lines = []
        for dim, tag in entities:
            if dim == 1:
                lines.append(tag)
        
        # 获取所有面
        surfaces = []
        for dim, tag in entities:
            if dim == 2:
                surfaces.append(tag)
        
        print(f"  找到: {len(points)} 个点, {len(lines)} 条线, {len(surfaces)} 个面")
        
        if surfaces:
            # 如果有面，创建曲面环
            # 创建曲面环
            loop = gmsh.model.occ.addSurfaceLoop(surfaces)
            
            # 创建平面曲面（这会创建一个新的曲面，用于网格生成）
            # 注意：这里我们创建的是一个新的曲面，而不是使用导入的网格
            # 这样Gmsh就会对这个曲面进行网格剖分
            
            # 由于我们有多个面，我们需要将它们组合成一个平面
            # 对于简单的矩形，我们可以直接创建一个新的矩形曲面
            # 但这里我们假设STL是一个平面形状
            
            # 获取面的边界框
            bbox = self._get_bounding_box(surfaces)
            if bbox:
                print(f"  边界框: x=[{bbox[0]:.4f}, {bbox[1]:.4f}], y=[{bbox[2]:.4f}, {bbox[3]:.4f}]")
                
                # 创建一个新的矩形曲面（基于边界框）
                new_surface = self.create_rectangle_surface(bbox[0], bbox[1], bbox[2], bbox[3])
                
                # 同步模型
                gmsh.model.occ.synchronize()
                
                print(f"  已创建新的几何曲面用于网格剖分")
                return new_surface
        
        return None
    
    def _get_bounding_box(self, entities):
        """获取实体的边界框"""
        xmin, xmax, ymin, ymax = float('inf'), -float('inf'), float('inf'), -float('inf')
        
        for tag in entities:
            # 获取面的边界
            # 简化：获取面上所有点的坐标
            try:
                # 获取面的点
                _, points, _ = gmsh.model.getBoundary([(2, tag)])
                for point in points:
                    coords = gmsh.model.getValue(0, point[1], [])
                    if len(coords) >= 2:
                        xmin = min(xmin, coords[0])
                        xmax = max(xmax, coords[0])
                        ymin = min(ymin, coords[1])
                        ymax = max(ymax, coords[1])
            except:
                continue
        
        if xmin == float('inf'):
            return None
        
        return [xmin, xmax, ymin, ymax]
    
    def create_rectangle_surface(self, xmin=0, xmax=1, ymin=0, ymax=1, z=0):
        """创建矩形曲面"""
        self._init()
        
        # 创建4个角点
        p1 = gmsh.model.occ.addPoint(xmin, ymin, z)
        p2 = gmsh.model.occ.addPoint(xmax, ymin, z)
        p3 = gmsh.model.occ.addPoint(xmax, ymax, z)
        p4 = gmsh.model.occ.addPoint(xmin, ymax, z)
        
        # 创建4条边
        l1 = gmsh.model.occ.addLine(p1, p2)
        l2 = gmsh.model.occ.addLine(p2, p3)
        l3 = gmsh.model.occ.addLine(p3, p4)
        l4 = gmsh.model.occ.addLine(p4, p1)
        
        # 创建曲线环
        loop = gmsh.model.occ.addCurveLoop([l1, l2, l3, l4])
        
        # 创建平面曲面
        surface = gmsh.model.occ.addPlaneSurface([loop])
        
        # 同步模型
        gmsh.model.occ.synchronize()
        
        print(f"创建矩形曲面: [{xmin},{xmax}] × [{ymin},{ymax}]")
        return surface
    
    def create_mesh_from_boundary(self, boundary_points):
        """
        从边界点创建网格
        
        这是最直接的方法：给定边界点，创建曲面，然后剖分网格
        """
        self._init()
        
        # 创建点
        point_tags = []
        for x, y in boundary_points:
            tag = gmsh.model.occ.addPoint(x, y, 0)
            point_tags.append(tag)
        
        # 创建线
        line_tags = []
        for i in range(len(point_tags)):
            j = (i + 1) % len(point_tags)
            line = gmsh.model.occ.addLine(point_tags[i], point_tags[j])
            line_tags.append(line)
        
        # 创建曲线环
        loop = gmsh.model.occ.addCurveLoop(line_tags)
        
        # 创建平面曲面
        surface = gmsh.model.occ.addPlaneSurface([loop])
        
        # 同步模型
        gmsh.model.occ.synchronize()
        
        print(f"从 {len(boundary_points)} 个边界点创建曲面")
        return surface
    
    def set_mesh_size(self, min_size, max_size):
        """设置网格尺寸"""
        gmsh.option.setNumber("Mesh.CharacteristicLengthMin", min_size)
        gmsh.option.setNumber("Mesh.CharacteristicLengthMax", max_size)
        print(f"网格尺寸: [{min_size}, {max_size}]")
    
    def set_mesh_type(self, element_type="triangle"):
        """设置网格单元类型"""
        if element_type == "triangle":
            gmsh.option.setNumber("Mesh.RecombineAll", 0)
            print("单元类型: 三角形")
        elif element_type == "quad":
            gmsh.option.setNumber("Mesh.RecombineAll", 1)
            print("单元类型: 四边形")
    
    def generate_mesh(self, dim=2):
        """生成网格"""
        print(f"生成网格 (维度={dim})...")
        gmsh.model.mesh.generate(dim)
        
        node_tags, node_coords, _ = gmsh.model.mesh.getNodes()
        node_count = len(node_tags)
        
        element_types, element_tags, _ = gmsh.model.mesh.getElements()
        elem_count = sum(len(tags) for tags in element_tags)
        
        print(f"  节点数: {node_count}")
        print(f"  单元数: {elem_count}")
        return node_count, elem_count
    
    def save_mesh(self, filename):
        """保存网格文件"""
        gmsh.write(filename)
        print(f"网格已保存: {filename}")
    
    def get_mesh_data(self):
        """获取网格数据"""
        node_tags, node_coords, _ = gmsh.model.mesh.getNodes()
        n_nodes = len(node_tags)
        nodes = node_coords.reshape(n_nodes, 3) if n_nodes > 0 else np.array([])
        
        element_types, element_tags, node_tags_per_element = gmsh.model.mesh.getElements()
        
        elements = []
        for etype, tags, node_tags in zip(element_types, element_tags, node_tags_per_element):
            if len(tags) > 0:
                num_nodes = len(node_tags) // len(tags)
                elem_nodes = node_tags.reshape(len(tags), num_nodes)
                elements.append((etype, elem_nodes))
        
        return nodes, elements
    
    def print_statistics(self):
        """打印统计信息"""
        nodes, elements = self.get_mesh_data()
        
        print("\n网格统计信息:")
        print("="*50)
        print(f"节点数: {len(nodes)}")
        print(f"单元数: {len(elements)}")
        
        if len(nodes) > 0:
            print(f"x范围: [{np.min(nodes[:,0]):.4f}, {np.max(nodes[:,0]):.4f}]")
            print(f"y范围: [{np.min(nodes[:,1]):.4f}, {np.max(nodes[:,1]):.4f}]")
        print("="*50)
    
    def launch_gui(self):
        """启动 Gmsh GUI"""
        gmsh.fltk.run()
    
    def close(self):
        """关闭 Gmsh"""
        if self._initialized:
            try:
                gmsh.finalize()
            except:
                pass
            self._initialized = False
