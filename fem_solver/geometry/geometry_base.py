"""
几何基类 - 定义几何的统一接口
"""

from abc import ABC, abstractmethod


class Geometry(ABC):
    """几何抽象基类"""
    
    def __init__(self, name="Geometry"):
        self.name = name
        
    @abstractmethod
    def export_to_stl(self, filename):
        """导出为STL文件"""
        pass
    
    def get_bounding_box(self):
        """获取包围盒（可选实现）"""
        return None