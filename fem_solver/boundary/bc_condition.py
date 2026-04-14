"""边界条件类定义"""

from enum import Enum
from typing import Callable


class BCType(Enum):
    DIRICHLET = 1
    NEUMANN = 2
    ROBIN = 3


class BoundaryCondition:
    def __init__(self, bc_type: BCType, value_func: Callable, name: str = None):
        self.bc_type = bc_type
        self.value_func = value_func
        self.name = name or f"{bc_type.name}_BC"

    def get_value(self, x: float, y: float) -> float:
        return self.value_func(x, y)


class DirichletBC(BoundaryCondition):
    def __init__(self, value_func: Callable, name: str = "Dirichlet"):
        super().__init__(BCType.DIRICHLET, value_func, name)