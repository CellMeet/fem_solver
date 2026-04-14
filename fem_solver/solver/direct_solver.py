"""直接求解器（高斯消元法）"""

from .linear_solver import LinearSolver
import math

class DirectSolver(LinearSolver):
    """直接求解器"""
    
    def __init__(self):
        super().__init__("Direct Solver (Gaussian Elimination)")
    
    def solve(self, A, b):
        """
        高斯消元法求解
        
        参数:
        A: 系数矩阵（字典格式 {(i,j): val}）
        b: 右端项（列表）
        """
        n = len(b)
        
        # 转换为稠密矩阵
        A_dense = [[0.0] * n for _ in range(n)]
        for (i, j), val in A.items():
            A_dense[i][j] = val
        
        b_dense = b.copy()
        
        # 前向消元
        for i in range(n):
            # 选主元
            pivot = i
            max_val = abs(A_dense[i][i])
            for k in range(i+1, n):
                if abs(A_dense[k][i]) > max_val:
                    max_val = abs(A_dense[k][i])
                    pivot = k
            
            # 交换行
            if pivot != i:
                A_dense[i], A_dense[pivot] = A_dense[pivot], A_dense[i]
                b_dense[i], b_dense[pivot] = b_dense[pivot], b_dense[i]
            
            # 检查奇异
            if abs(A_dense[i][i]) < 1e-12:
                print(f"警告: 矩阵奇异，第{i}行主元为0")
                continue
            
            # 消元
            for k in range(i+1, n):
                if abs(A_dense[k][i]) < 1e-15:
                    continue
                factor = A_dense[k][i] / A_dense[i][i]
                for j in range(i, n):
                    A_dense[k][j] -= factor * A_dense[i][j]
                b_dense[k] -= factor * b_dense[i]
        
        # 回代
        u = [0.0] * n
        for i in range(n-1, -1, -1):
            sum_ax = 0.0
            for j in range(i+1, n):
                sum_ax += A_dense[i][j] * u[j]
            u[i] = (b_dense[i] - sum_ax) / A_dense[i][i]
        
        self.solution = u
        return u