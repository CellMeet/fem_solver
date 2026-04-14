"""
基本几何体 - 创建简单几何用于测试
"""

import math
import os
from .geometry_base import Geometry


class Rectangle(Geometry):
    """矩形几何"""
    
    def __init__(self, xmin=0, xmax=1, ymin=0, ymax=1, z=0):
        super().__init__("Rectangle")
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.z = z
        
    def export_to_stl(self, filename):
        """导出为STL文件（ASCII格式）"""
        x1, x2 = self.xmin, self.xmax
        y1, y2 = self.ymin, self.ymax
        z = self.z
        
        with open(filename, 'w') as f:
            f.write("solid rectangle\n")
            
            # 第一个三角形（左下-右下-右上）
            f.write("facet normal 0 0 1\n")
            f.write("  outer loop\n")
            f.write(f"    vertex {x1} {y1} {z}\n")
            f.write(f"    vertex {x2} {y1} {z}\n")
            f.write(f"    vertex {x2} {y2} {z}\n")
            f.write("  endloop\n")
            f.write("endfacet\n")
            
            # 第二个三角形（左下-右上-左上）
            f.write("facet normal 0 0 1\n")
            f.write("  outer loop\n")
            f.write(f"    vertex {x1} {y1} {z}\n")
            f.write(f"    vertex {x2} {y2} {z}\n")
            f.write(f"    vertex {x1} {y2} {z}\n")
            f.write("  endloop\n")
            f.write("endfacet\n")
            
            f.write("endsolid rectangle\n")
        
        return filename
    
    def get_bounding_box(self):
        """获取包围盒"""
        return {
            'x': (self.xmin, self.xmax),
            'y': (self.ymin, self.ymax),
            'z': (self.z, self.z)
        }


class Circle(Geometry):
    """圆形几何"""
    
    def __init__(self, xc=0, yc=0, radius=1, z=0, segments=32):
        super().__init__("Circle")
        self.xc = xc
        self.yc = yc
        self.radius = radius
        self.z = z
        self.segments = segments
        
    def export_to_stl(self, filename):
        """导出为STL文件"""
        vertices = []
        
        # 创建圆上的点
        for i in range(self.segments):
            angle = 2 * math.pi * i / self.segments
            x = self.xc + self.radius * math.cos(angle)
            y = self.yc + self.radius * math.sin(angle)
            vertices.append((x, y, self.z))
        
        with open(filename, 'w') as f:
            f.write("solid circle\n")
            
            # 创建三角形（圆心 + 相邻两点）
            for i in range(self.segments):
                j = (i + 1) % self.segments
                
                f.write("facet normal 0 0 1\n")
                f.write("  outer loop\n")
                f.write(f"    vertex {self.xc} {self.yc} {self.z}\n")
                f.write(f"    vertex {vertices[i][0]} {vertices[i][1]} {vertices[i][2]}\n")
                f.write(f"    vertex {vertices[j][0]} {vertices[j][1]} {vertices[j][2]}\n")
                f.write("  endloop\n")
                f.write("endfacet\n")
            
            f.write("endsolid circle\n")
        
        return filename
    
    def get_bounding_box(self):
        """获取包围盒"""
        return {
            'x': (self.xc - self.radius, self.xc + self.radius),
            'y': (self.yc - self.radius, self.yc + self.radius),
            'z': (self.z, self.z)
        }