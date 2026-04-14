"""迭代求解器（共轭梯度法）"""

from .linear_solver import LinearSolver
import math

class ConjugateGradientSolver(LinearSolver):
    """共轭梯度法求解器（适用于对称正定矩阵）"""
    
    def __init__(self, max_iter=5000, tol=1e-6):
        super().__init__("Conjugate Gradient Solver")
        self.max_iter = max_iter
        self.tol = tol
    
    def solve(self, A, b):
        """
        共轭梯度法求解
        
        参数:
        A: 系数矩阵（字典格式）
        b: 右端项
        """
        n = len(b)
        
        # 初始化
        x = [0.0] * n
        r = b[:]
        
        # 计算初始残差
        for i in range(n):
            for j in range(n):
                if (i, j) in A:
                    r[i] -= A[(i, j)] * x[j]
        
        p = r[:]
        rsold = sum(ri * ri for ri in r)
        
        for iteration in range(self.max_iter):
            # 计算 A*p
            Ap = [0.0] * n
            for i in range(n):
                for j in range(n):
                    if (i, j) in A:
                        Ap[i] += A[(i, j)] * p[j]
            
            # 计算步长
            pAp = sum(p[i] * Ap[i] for i in range(n))
            if abs(pAp) < 1e-15:
                break
            
            alpha = rsold / pAp
            
            # 更新解和残差
            for i in range(n):
                x[i] += alpha * p[i]
                r[i] -= alpha * Ap[i]
            
            # 计算新的残差范数
            rsnew = sum(ri * ri for ri in r)
            
            # 检查收敛
            if math.sqrt(rsnew) < self.tol:
                print(f"  共轭梯度法收敛，迭代次数: {iteration + 1}")
                break
            
            # 更新搜索方向
            beta = rsnew / rsold
            for i in range(n):
                p[i] = r[i] + beta * p[i]
            
            rsold = rsnew
        else:
            print(f"  警告: 共轭梯度法未收敛，最大迭代次数: {self.max_iter}")
        
        self.solution = x
        return x