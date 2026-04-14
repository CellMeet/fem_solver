"""材料属性管理"""

class Material:
    """材料基类"""
    
    def __init__(self, name):
        self.name = name
    
    def get_c(self, x, y):
        """扩散系数 c(x,y)"""
        return 1.0
    
    def get_rho(self, x, y):
        """密度 ρ(x,y)"""
        return 1.0
    
    def get_k(self, x, y):
        """波数 k(x,y)"""
        return 1.0


class ConstantMaterial(Material):
    """常数材料"""
    
    def __init__(self, name, c=1.0, rho=1.0, k=1.0):
        super().__init__(name)
        self.c_val = c
        self.rho_val = rho
        self.k_val = k
    
    def get_c(self, x, y, z=None):
        return self.c_val
    
    def get_rho(self, x, y, z=None):
        return self.rho_val
    
    def get_k(self, x, y, z=None):
        return self.k_val


class VariableMaterial(Material):
    """变系数材料"""
    
    def __init__(self, name, c_func, rho_func=None, k_func=None):
        super().__init__(name)
        self.c_func = c_func
        self.rho_func = rho_func or (lambda x, y: 1.0)
        self.k_func = k_func or (lambda x, y: 1.0)
    
    def get_c(self, x, y):
        return self.c_func(x, y)
    
    def get_rho(self, x, y):
        return self.rho_func(x, y)
    
    def get_k(self, x, y):
        return self.k_func(x, y)