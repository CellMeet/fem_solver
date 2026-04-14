# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个模块化的有限元求解器（FEM Solver），用于求解偏微分方程（如 Poisson 方程、静电场问题等）。代码支持 2D 和 3D 几何，包含从几何建模、网格生成、方程组装到求解和后处理的完整工作流。

## 核心架构

### 主求解流程

1. **几何建模** (`geometry/`)：从 STL 文件读取几何或使用原始几何（矩形、球体、圆柱等）
2. **网格生成** (`meshing/`)：使用 Gmsh 生成三角形/四面体网格
3. **材料定义** (`material/`)：设置材料属性（常数或空间变化）
4. **边界条件** (`boundary/`)：应用 Dirichlet、Neumann 或 Robin 边界条件
5. **矩阵组装** (`assembly/`)：组装全局刚度矩阵、质量矩阵和载荷向量
6. **求解** (`solver/`)：使用直接法（高斯消元）或迭代法（共轭梯度）求解线性系统
7. **后处理** (`postprocess/`)：输出 VTK 和文本格式的结果

### 关键组件关系

```
FEMSolver (main.py)
    ├─> Mesh (core/mesh.py) - 管理节点和单元
    ├─> Material (material/material.py) - 材料属性
    ├─> BCManager (boundary/bc_manager.py) - 边界条件管理
    ├─> Assembler (assembly/assembler.py) - 全局矩阵组装
    └─> Solver (solver/) - 线性系统求解
```

### 稀疏矩阵格式

- 全局刚度矩阵 `A` 和质量矩阵 `M` 使用字典存储：`{(i, j): value}`
- 只存储非零元素以节省内存
- 边界条件应用时使用"置大数法"（big number method）

### 边界条件应用

边界条件通过几何标识（'left', 'right', 'top', 'bottom'）自动识别节点：
- `BCManager.apply_all()` 根据网格边界自动识别并应用边界条件
- 支持直接指定节点边界值：`add_dirichlet_node(node_id, value)`

## 运行示例

### 运行内置示例
```bash
# 2D Poisson 方程示例
python main.py

# 完整工作流示例（几何 → 网格 → 求解）
python examples/complete_workflow.py

# 3D 静电场示例
python examples/electrostatic_3d.py

# 3D 网格生成示例
python examples/mesh_3d_universal.py
```

### 编写自定义求解脚本

```python
from fem_solver import FEMSolver, ConstantMaterial
import math

# 创建求解器
solver = FEMSolver()
solver.create_mesh(0, 1, 0, 1, nx=40, ny=40)
solver.set_material(ConstantMaterial("材料", c=1.0))

# 定义边界条件
solver.add_dirichlet_bc('left', lambda x, y: 0.0)
solver.add_dirichlet_bc('right', lambda x, y: 0.0)

# 定义源项并求解
solution = solver.solve(lambda x, y: math.sin(math.pi * x))

# 保存结果
solver.save_results("output.vtk", "output.txt")
```

## 依赖项

核心依赖：
- **gmsh** - 网格生成（用于复杂几何）
- **numpy** - 数值计算（部分模块使用）

可选依赖：
- **matplotlib** - 可视化（用于 `plot_centerline.py` 等）

注意：大部分核心功能（矩阵组装、求解器）使用纯 Python 实现，不依赖 NumPy/SciPy。

## 模块路径问题

示例代码需要将项目根目录添加到 `sys.path`：
```python
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
```

## 3D 网格与求解

- 3D 网格使用 `GmshMesher` 类（`meshing/gmsh_mesher.py`）
- 3D 单元类型：四面体（Tetrahedron）
- 3D 边界条件需要处理曲面而非曲线
- 查看 `examples/electrostatic_3d.py` 了解完整的 3D 求解流程

## 代码约定

- 节点 ID 和单元 ID 从 0 开始
- 三角形单元顶点按逆时针顺序定义
- 边界条件函数签名：`func(x, y)` 或 `func(x, y, z)`
- 材料属性函数签名：`func(x, y)` 返回系数值
