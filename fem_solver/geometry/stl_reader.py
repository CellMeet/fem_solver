"""
STL文件读取器
"""

import numpy as np
import struct
import os
from .geometry_base import Geometry


class STLReader(Geometry):
    """STL文件读取器"""
    
    def __init__(self, filename=None):
        super().__init__("STL Geometry")
        self.filename = filename
        self.vertices = []
        self.triangles = []
        self.bounding_box = None
        
        if filename and os.path.exists(filename):
            self.read_stl(filename)
    
    def read_stl(self, filename):
        """读取STL文件"""
        self.filename = filename
        
        # 判断是ASCII还是二进制
        with open(filename, 'rb') as f:
            header = f.read(80)
            is_ascii = self._is_ascii(header)
        
        if is_ascii:
            self._read_ascii(filename)
        else:
            self._read_binary(filename)
        
        self._update_bounding_box()
        print(f"读取STL: {filename}")
        print(f"  三角形数量: {len(self.triangles)}")
        print(f"  顶点数量: {len(self.vertices)}")
    
    def _is_ascii(self, header):
        """判断是否为ASCII格式"""
        try:
            header_str = header.decode('ascii').strip()
            return header_str.startswith('solid')
        except:
            return False
    
    def _read_ascii(self, filename):
        """读取ASCII格式STL"""
        with open(filename, 'r') as f:
            lines = f.readlines()
        
        vertices_set = set()
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith('facet'):
                # 找到 outer loop
                while i < len(lines) and 'outer loop' not in lines[i]:
                    i += 1
                i += 1
                
                # 读取三个顶点
                tri_vertices = []
                for _ in range(3):
                    while i < len(lines) and not lines[i].strip().startswith('vertex'):
                        i += 1
                    parts = lines[i].strip().split()
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    tri_vertices.append((x, y, z))
                    vertices_set.add((x, y, z))
                    i += 1
                
                self.triangles.append(tri_vertices)
            
            i += 1
        
        self.vertices = list(vertices_set)
    
    def _read_binary(self, filename):
        """读取二进制格式STL"""
        with open(filename, 'rb') as f:
            f.seek(80)
            num_triangles = struct.unpack('<I', f.read(4))[0]
            
            vertices_set = set()
            
            for _ in range(num_triangles):
                # 跳过法向量
                f.read(12)
                
                # 读取三个顶点
                tri_vertices = []
                for _ in range(3):
                    x, y, z = struct.unpack('<fff', f.read(12))
                    tri_vertices.append((x, y, z))
                    vertices_set.add((x, y, z))
                
                self.triangles.append(tri_vertices)
                f.read(2)  # 属性字节
            
            self.vertices = list(vertices_set)
    
    def _update_bounding_box(self):
        """更新包围盒"""
        if not self.vertices:
            return
        
        xs = [v[0] for v in self.vertices]
        ys = [v[1] for v in self.vertices]
        zs = [v[2] for v in self.vertices]
        
        self.bounding_box = {
            'x': (min(xs), max(xs)),
            'y': (min(ys), max(ys)),
            'z': (min(zs), max(zs))
        }
    
    def export_to_stl(self, filename):
        """导出为STL（复制原文件）"""
        import shutil
        if self.filename:
            shutil.copy(self.filename, filename)
            print(f"已导出: {filename}")
    
    def get_bounding_box(self):
        """获取包围盒"""
        return self.bounding_box
    
    def get_mesh_data(self):
        """获取用于网格生成的数据"""
        return {
            'points': self.vertices,
            'triangles': self.triangles,
            'bounding_box': self.bounding_box
        }