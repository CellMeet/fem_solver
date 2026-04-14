"""
3D几何体 - 用于生成测试STL文件
"""

import math


class Sphere:
    """球体几何"""
    
    def __init__(self, xc=0, yc=0, zc=0, radius=1, segments=32):
        self.xc = xc
        self.yc = yc
        self.zc = zc
        self.radius = radius
        self.segments = segments
    
    def export_to_stl(self, filename):
        """
        导出球体为STL文件（使用三角形面片）
        
        使用经纬度方法生成球体表面
        """
        vertices = []
        
        # 生成顶点
        for i in range(self.segments + 1):
            theta = i * math.pi / self.segments  # 极角 (0 到 pi)
            sin_theta = math.sin(theta)
            cos_theta = math.cos(theta)
            
            for j in range(self.segments + 1):
                phi = j * 2 * math.pi / self.segments  # 方位角 (0 到 2pi)
                sin_phi = math.sin(phi)
                cos_phi = math.cos(phi)
                
                x = self.xc + self.radius * sin_theta * cos_phi
                y = self.yc + self.radius * sin_theta * sin_phi
                z = self.zc + self.radius * cos_theta
                vertices.append((x, y, z))
        
        # 生成三角形面片
        triangles = []
        for i in range(self.segments):
            for j in range(self.segments):
                # 四个顶点索引
                p1 = i * (self.segments + 1) + j
                p2 = i * (self.segments + 1) + j + 1
                p3 = (i + 1) * (self.segments + 1) + j
                p4 = (i + 1) * (self.segments + 1) + j + 1
                
                # 两个三角形组成一个矩形面
                triangles.append((p1, p2, p3))
                triangles.append((p2, p4, p3))
        
        # 写入STL文件
        with open(filename, 'w') as f:
            f.write("solid sphere\n")
            for tri in triangles:
                # 计算法向量（简化：使用第一个顶点）
                v1 = vertices[tri[0]]
                v2 = vertices[tri[1]]
                v3 = vertices[tri[2]]
                
                # 计算法向量
                ux = v2[0] - v1[0]
                uy = v2[1] - v1[1]
                uz = v2[2] - v1[2]
                vx = v3[0] - v1[0]
                vy = v3[1] - v1[1]
                vz = v3[2] - v1[2]
                
                nx = uy * vz - uz * vy
                ny = uz * vx - ux * vz
                nz = ux * vy - uy * vx
                
                # 归一化
                length = math.sqrt(nx*nx + ny*ny + nz*nz)
                if length > 0:
                    nx /= length
                    ny /= length
                    nz /= length
                
                f.write(f"facet normal {nx} {ny} {nz}\n")
                f.write("  outer loop\n")
                for idx in tri:
                    f.write(f"    vertex {vertices[idx][0]} {vertices[idx][1]} {vertices[idx][2]}\n")
                f.write("  endloop\n")
                f.write("endfacet\n")
            f.write("endsolid sphere\n")
        
        print(f"创建球体STL: {filename}")
        print(f"  顶点数: {len(vertices)}")
        print(f"  三角形面片数: {len(triangles)}")
        return filename


class Cube:
    """立方体几何"""
    
    def __init__(self, xmin=0, xmax=1, ymin=0, ymax=1, zmin=0, zmax=1):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.zmin = zmin
        self.zmax = zmax
    
    def export_to_stl(self, filename):
        """导出立方体为STL文件"""
        x1, x2 = self.xmin, self.xmax
        y1, y2 = self.ymin, self.ymax
        z1, z2 = self.zmin, self.zmax
        
        # 立方体的8个顶点
        vertices = [
            (x1, y1, z1), (x2, y1, z1), (x2, y2, z1), (x1, y2, z1),  # 底面
            (x1, y1, z2), (x2, y1, z2), (x2, y2, z2), (x1, y2, z2)   # 顶面
        ]
        
        # 6个面的三角形划分（每个面2个三角形）
        faces = [
            # 底面 (z = z1)
            [(0, 1, 2), (0, 2, 3)],
            # 顶面 (z = z2)
            [(4, 6, 5), (4, 7, 6)],
            # 前面 (y = y1)
            [(0, 4, 5), (0, 5, 1)],
            # 后面 (y = y2)
            [(3, 2, 6), (3, 6, 7)],
            # 左面 (x = x1)
            [(0, 3, 7), (0, 7, 4)],
            # 右面 (x = x2)
            [(1, 5, 6), (1, 6, 2)]
        ]
        
        with open(filename, 'w') as f:
            f.write("solid cube\n")
            for face in faces:
                for tri in face:
                    v1 = vertices[tri[0]]
                    v2 = vertices[tri[1]]
                    v3 = vertices[tri[2]]
                    
                    # 计算法向量
                    ux = v2[0] - v1[0]
                    uy = v2[1] - v1[1]
                    uz = v2[2] - v1[2]
                    vx = v3[0] - v1[0]
                    vy = v3[1] - v1[1]
                    vz = v3[2] - v1[2]
                    
                    nx = uy * vz - uz * vy
                    ny = uz * vx - ux * vz
                    nz = ux * vy - uy * vx
                    
                    # 归一化
                    length = math.sqrt(nx*nx + ny*ny + nz*nz)
                    if length > 0:
                        nx /= length
                        ny /= length
                        nz /= length
                    
                    f.write(f"facet normal {nx} {ny} {nz}\n")
                    f.write("  outer loop\n")
                    f.write(f"    vertex {v1[0]} {v1[1]} {v1[2]}\n")
                    f.write(f"    vertex {v2[0]} {v2[1]} {v2[2]}\n")
                    f.write(f"    vertex {v3[0]} {v3[1]} {v3[2]}\n")
                    f.write("  endloop\n")
                    f.write("endfacet\n")
            f.write("endsolid cube\n")
        
        print(f"创建立方体STL: {filename}")
        return filename


class Cylinder:
    """圆柱体几何"""
    
    def __init__(self, xc=0, yc=0, radius=1, height=2, segments=32):
        self.xc = xc
        self.yc = yc
        self.radius = radius
        self.height = height
        self.segments = segments
        self.z_bottom = -height/2
        self.z_top = height/2
    
    def export_to_stl(self, filename):
        """导出圆柱体为STL文件"""
        vertices = []
        
        # 底面和顶面的点
        for i in range(self.segments):
            angle = 2 * math.pi * i / self.segments
            x = self.xc + self.radius * math.cos(angle)
            y = self.yc + self.radius * math.sin(angle)
            vertices.append((x, y, self.z_bottom))  # 底面
            vertices.append((x, y, self.z_top))     # 顶面
        
        # 中心点
        center_bottom = (self.xc, self.yc, self.z_bottom)
        center_top = (self.xc, self.yc, self.z_top)
        
        with open(filename, 'w') as f:
            f.write("solid cylinder\n")
            
            # 底面三角形
            for i in range(self.segments):
                j = (i + 1) % self.segments
                p1 = 2 * i
                p2 = 2 * j
                
                # 底面三角形
                self._write_triangle(f, center_bottom, vertices[p1], vertices[p2])
                
                # 顶面三角形
                p1_top = 2 * i + 1
                p2_top = 2 * j + 1
                self._write_triangle(f, center_top, vertices[p1_top], vertices[p2_top])
                
                # 侧面四边形（分成两个三角形）
                self._write_triangle(f, vertices[p1], vertices[p2], vertices[p2_top])
                self._write_triangle(f, vertices[p1], vertices[p2_top], vertices[p1_top])
            
            f.write("endsolid cylinder\n")
        
        print(f"创建圆柱体STL: {filename}")
        return filename
    
    def _write_triangle(self, f, v1, v2, v3):
        """写入三角形面片"""
        # 计算法向量
        ux = v2[0] - v1[0]
        uy = v2[1] - v1[1]
        uz = v2[2] - v1[2]
        vx = v3[0] - v1[0]
        vy = v3[1] - v1[1]
        vz = v3[2] - v1[2]
        
        nx = uy * vz - uz * vy
        ny = uz * vx - ux * vz
        nz = ux * vy - uy * vx
        
        length = math.sqrt(nx*nx + ny*ny + nz*nz)
        if length > 0:
            nx /= length
            ny /= length
            nz /= length
        
        f.write(f"facet normal {nx} {ny} {nz}\n")
        f.write("  outer loop\n")
        f.write(f"    vertex {v1[0]} {v1[1]} {v1[2]}\n")
        f.write(f"    vertex {v2[0]} {v2[1]} {v2[2]}\n")
        f.write(f"    vertex {v3[0]} {v3[1]} {v3[2]}\n")
        f.write("  endloop\n")
        f.write("endfacet\n")
