"""线性求解器基类"""

from abc import ABC, abstractmethod

class LinearSolver(ABC):
    """线性求解器抽象基类"""
    
    def __init__(self, name):
        self.name = name
        self.solution = None
    
    @abstractmethod
    def solve(self, A, b):
        """求解线性方程组 A x = b"""
        pass
    
    def get_solution(self):
        return self.solution