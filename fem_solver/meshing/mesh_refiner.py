"""
网格细化器 - 自适应网格细化
"""

import numpy as np


class MeshRefiner:
    """
    网格细化器
    
    基于误差指示器的自适应网格细化
    """
    
    def __init__(self, mesh, solution):
        """
        初始化细化器
        
        参数:
            mesh: 网格对象
            solution: 节点解
        """
        self.mesh = mesh
        self.solution = solution
        self.error_indicators = None
    
    def compute_error_indicator(self, gradient=False):
        """
        计算误差指示器
        
        参数:
            gradient: 是否使用梯度误差
        """
        self.error_indicators = []
        
        for element in self.mesh.elements:
            if gradient:
                # 基于梯度的误差指示
                error = self._compute_gradient_error(element)
            else:
                # 基于残差的误差指示
                error = self._compute_residual_error(element)
            
            self.error_indicators.append((element.id, error))
        
        return self.error_indicators
    
    def _compute_gradient_error(self, element):
        """计算梯度误差"""
        # 获取单元节点解
        u = [self.solution[node.id] for node in element.nodes]
        
        # 计算单元内梯度变化
        # 简化实现：用节点值的标准差作为误差指示
        u_mean = np.mean(u)
        error = np.std(u)
        
        return error
    
    def _compute_residual_error(self, element):
        """计算残差误差"""
        # 简化实现
        return 1.0
    
    def refine_by_percentage(self, percentage=20):
        """
        按百分比细化网格
        
        参数:
            percentage: 细化百分比（误差最大的单元）
        """
        if not self.error_indicators:
            self.compute_error_indicator()
        
        # 按误差排序
        sorted_errors = sorted(self.error_indicators, 
                               key=lambda x: x[1], reverse=True)
        
        # 选择需要细化的单元
        n_refine = int(len(sorted_errors) * percentage / 100)
        refine_ids = [elem_id for elem_id, _ in sorted_errors[:n_refine]]
        
        print(f"选择 {len(refine_ids)} 个单元进行细化")
        return refine_ids