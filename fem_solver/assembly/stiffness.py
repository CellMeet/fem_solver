"""
单元刚度矩阵计算函数
"""

import numpy as np


def compute_triangle_stiffness(nodes, material, xyz=None):
    """
    计算三角形单元刚度矩阵 (2D)
    nodes: 3个节点对象
    material: 材料对象，需提供 get_c(x,y) 方法
    """
    x = [n.x for n in nodes]
    y = [n.y for n in nodes]
    area = abs((x[0]*(y[1]-y[2]) + x[1]*(y[2]-y[0]) + x[2]*(y[0]-y[1])) / 2.0)
    # 形函数梯度 (常数)
    b = np.zeros(3)
    c = np.zeros(3)
    for i in range(3):
        j = (i+1)%3
        k = (i+2)%3
        b[i] = (y[j] - y[k]) / (2.0*area)
        c[i] = (x[k] - x[j]) / (2.0*area)
    # 材料系数 (取形心)
    cx = sum(x)/3.0
    cy = sum(y)/3.0
    c_val = material.get_c(cx, cy)
    Ke = np.zeros((3,3))
    for i in range(3):
        for j in range(3):
            Ke[i,j] = c_val * area * (b[i]*b[j] + c[i]*c[j])
    return Ke


def compute_tetrahedron_stiffness(nodes, material, xyz=None):
    """
    计算四面体单元刚度矩阵 (3D)
    nodes: 4个节点对象
    material: 材料对象，需提供 get_c(x,y,z) 方法
    """
    # 节点坐标数组 (4,3)
    pts = np.array([[n.x, n.y, n.z] for n in nodes])
    # 体积
    v1 = pts[1] - pts[0]
    v2 = pts[2] - pts[0]
    v3 = pts[3] - pts[0]
    vol = abs(np.dot(v1, np.cross(v2, v3))) / 6.0
    if vol < 1e-15:
        raise ValueError("单元体积为零或负")
    # 形函数梯度 (4x3)
    A = np.column_stack((np.ones(4), pts))
    invA = np.linalg.inv(A)
    grads = invA[:, 1:4]   # 每行 (bx, by, bz)
    # 材料系数 (取形心)
    centroid = np.mean(pts, axis=0)
    c_val = material.get_c(centroid[0], centroid[1], centroid[2])
    Ke = c_val * vol * (grads @ grads.T)
    return Ke


# 可根据单元类型分派
def compute_stiffness(element, material):
    """
    通用入口，根据单元节点数自动选择
    """
    n_nodes = len(element.nodes)
    if n_nodes == 3:
        return compute_triangle_stiffness(element.nodes, material)
    elif n_nodes == 4:
        return compute_tetrahedron_stiffness(element.nodes, material)
    else:
        raise NotImplementedError(f"不支持 {n_nodes} 节点单元")