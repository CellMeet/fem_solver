"""
网格格式转换器 - 在不同网格格式间转换
"""

import meshio
import numpy as np


class MeshConverter:
    """
    网格格式转换器
    """
    
    @staticmethod
    def convert(input_file, output_file, output_format=None):
        """
        转换网格格式
        
        参数:
            input_file: 输入文件路径
            output_file: 输出文件路径
            output_format: 输出格式（自动从扩展名判断）
        """
        mesh = meshio.read(input_file)
        meshio.write(output_file, mesh)
        print(f"转换完成: {input_file} -> {output_file}")
    
    @staticmethod
    def extract_surface(mesh_file, output_file):
        """
        从体网格提取表面网格
        
        参数:
            mesh_file: 输入体网格文件
            output_file: 输出表面网格文件
        """
        mesh = meshio.read(mesh_file)
        
        # 提取表面三角形单元
        surface_cells = []
        for cell_type, data in mesh.cells:
            if cell_type == "triangle":
                surface_cells.append((cell_type, data))
        
        surface_mesh = meshio.Mesh(
            points=mesh.points,
            cells=surface_cells,
            point_data=mesh.point_data
        )
        
        meshio.write(output_file, surface_mesh)
        print(f"表面网格已提取: {output_file}")
    
    @staticmethod
    def merge_meshes(mesh_files, output_file):
        """
        合并多个网格文件
        
        参数:
            mesh_files: 网格文件列表
            output_file: 输出文件
        """
        all_points = []
        all_cells = []
        point_offset = 0
        
        for fname in mesh_files:
            mesh = meshio.read(fname)
            
            # 合并节点
            new_points = mesh.points + point_offset
            all_points.extend(new_points)
            
            # 合并单元
            for cell_type, data in mesh.cells:
                new_data = data + point_offset
                all_cells.append((cell_type, new_data))
            
            point_offset += len(mesh.points)
        
        merged_mesh = meshio.Mesh(
            points=np.array(all_points),
            cells=all_cells
        )
        
        meshio.write(output_file, merged_mesh)
        print(f"合并完成: {len(mesh_files)} 个文件 -> {output_file}")