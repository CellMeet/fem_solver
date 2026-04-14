"""
单元载荷向量计算函数
"""

import numpy as np


def compute_triangle_load(nodes, source_func):
    """三角形单元载荷向量 (2D)"""
    x = [n.x for n in nodes]
    y = [n.y for n in nodes]
    area = abs((x[0]*(y[1]-y[2]) + x[1]*(y[2]-y[0]) + x[2]*(y[0]-y[1])) / 2.0)
    cx = sum(x)/3.0
    cy = sum(y)/3.0
    f_center = source_func(cx, cy, 0)  # 2D问题z=0
    fe = np.full(3, f_center * area / 3.0)
    return fe


def compute_tetrahedron_load(nodes, source_func):
    """四面体单元载荷向量 (3D)"""
    pts = np.array([[n.x, n.y, n.z] for n in nodes])
    v1 = pts[1] - pts[0]
    v2 = pts[2] - pts[0]
    v3 = pts[3] - pts[0]
    vol = abs(np.dot(v1, np.cross(v2, v3))) / 6.0
    centroid = np.mean(pts, axis=0)
    f_center = source_func(centroid[0], centroid[1], centroid[2])
    fe = np.full(4, f_center * vol / 4.0)
    return fe


def compute_load(element, source_func):
    n_nodes = len(element.nodes)
    if n_nodes == 3:
        return compute_triangle_load(element.nodes, source_func)
    elif n_nodes == 4:
        return compute_tetrahedron_load(element.nodes, source_func)
    else:
        raise NotImplementedError(f"不支持 {n_nodes} 节点单元")