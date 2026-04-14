"""
Gmsh 3D网格生成器 - 从STL生成四面体网格
"""

import gmsh
import numpy as np
import os


class Gmsh3DGenerator:
    """
    通用3D网格生成器 - 从STL生成体网格
    """
    
    def __init__(self):
        self._initialized = False
        self.model_name = None
        
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
        self.model_name = name
        print(f"创建模型: {name}")
    
    def mesh_from_stl(self, stl_file, mesh_size=0.1, optimize=True):
        """
        从STL文件生成3D四面体网格
        """
        if not os.path.exists(stl_file):
            raise FileNotFoundError(f"STL文件不存在: {stl_file}")
        
        self._init()
        
        print(f"\n{'='*60}")
        print(f"从STL生成3D四面体网格")
        print(f"文件: {stl_file}")
        print(f"网格尺寸: {mesh_size}")
        print(f"{'='*60}")
        
        try:
            # 步骤1: 导入STL
            print("\n[步骤1] 导入STL文件...")
            gmsh.merge(stl_file)
            
            # 步骤2: 分类曲面（使用45度角，确保封闭曲面被识别）
            print("\n[步骤2] 分类曲面...")
            gmsh.model.mesh.classifySurfaces(45.0, True, True)
            
            # 步骤3: 创建几何（从离散网格创建几何实体）
            print("\n[步骤3] 创建几何...")
            gmsh.model.mesh.createGeometry()
            
            # 步骤4: 获取所有几何曲面
            entities = gmsh.model.getEntities()
            surfaces = [tag for dim, tag in entities if dim == 2]
            if not surfaces:
                print("  错误: 没有找到曲面")
                return False, 0, 0
            print(f"  找到 {len(surfaces)} 个曲面")
            
            # 步骤5: 使用 OpenCASCADE 创建体
            print("\n[步骤4] 创建体...")
            # 创建曲面环
            loop = gmsh.model.occ.addSurfaceLoop(surfaces)
            # 创建体
            volume = gmsh.model.occ.addVolume([loop])
            gmsh.model.occ.synchronize()
            print("  体创建成功")
            
            # 步骤6: 设置网格参数
            print("\n[步骤5] 设置网格参数...")
            gmsh.option.setNumber("Mesh.CharacteristicLengthMin", mesh_size)
            gmsh.option.setNumber("Mesh.CharacteristicLengthMax", mesh_size)
            print(f"  网格尺寸: {mesh_size}")
            
            # 步骤7: 生成体网格
            print("\n[步骤6] 生成四面体网格...")
            gmsh.model.mesh.generate(3)
            
            # 步骤8: 优化网格
            if optimize:
                print("\n[步骤7] 优化网格质量...")
                gmsh.model.mesh.optimize("Netgen")
                print("  网格优化完成")
            
            # 步骤9: 统计
            node_tags, node_coords, _ = gmsh.model.mesh.getNodes()
            node_count = len(node_tags)
            
            element_types, element_tags, _ = gmsh.model.mesh.getElements()
            elem_count = 0
            tet_count = 0
            tri_count = 0
            
            for etype, tags in zip(element_types, element_tags):
                elem_count += len(tags)
                if etype == 4:      # 四面体
                    tet_count += len(tags)
                elif etype == 2:    # 三角形
                    tri_count += len(tags)
            
            print(f"\n[步骤8] 网格统计:")
            print(f"  节点数: {node_count}")
            print(f"  总单元数: {elem_count}")
            print(f"  四面体单元: {tet_count} (3D)")
            print(f"  三角形单元: {tri_count} (2D)")
            
            if tet_count == 0:
                print("\n  ⚠️ 警告: 没有生成四面体单元！")
            else:
                print("\n  ✓ 成功生成3D四面体网格!")
            
            return True, node_count, elem_count
            
        except Exception as e:
            print(f"\n错误: {e}")
            import traceback
            traceback.print_exc()
            return False, 0, 0
    
    def save_mesh(self, filename):
        gmsh.write(filename)
        print(f"网格已保存: {filename}")
    
    def get_mesh_data(self):
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
        nodes, elements = self.get_mesh_data()
        print("\n网格统计信息:")
        print("="*50)
        print(f"节点数: {len(nodes)}")
        print(f"单元数: {len(elements)}")
        if len(nodes) > 0:
            print(f"x范围: [{np.min(nodes[:,0]):.4f}, {np.max(nodes[:,0]):.4f}]")
            print(f"y范围: [{np.min(nodes[:,1]):.4f}, {np.max(nodes[:,1]):.4f}]")
            print(f"z范围: [{np.min(nodes[:,2]):.4f}, {np.max(nodes[:,2]):.4f}]")
        print("="*50)
    
    def launch_gui(self):
        gmsh.fltk.run()
    
    def close(self):
        if self._initialized:
            try:
                gmsh.finalize()
            except:
                pass
            self._initialized = False
