from fem_solver.boundary.bc_manager import BCManager, find_boundary_nodes

def main():
    print("生成2D网格...")
    mesh_file = create_2d_mesh(mesh_size=0.02)
    points, cells, wire_elems = load_2d_mesh(mesh_file)

    from fem_solver.core.mesh import Mesh
    from fem_solver.core.node import Node
    from fem_solver.core.element import TriangleElement

    solver_mesh = Mesh()
    for i, (x, y) in enumerate(points):
        solver_mesh.nodes.append(Node(i, x, y, 0.0))
    solver_mesh.node_count = len(points)

    for eid, (n0, n1, n2) in enumerate(cells):
        nodes = [solver_mesh.nodes[n0], solver_mesh.nodes[n1], solver_mesh.nodes[n2]]
        elem = TriangleElement(eid, nodes)
        solver_mesh.elements.append(elem)
    solver_mesh.element_count = len(cells)

    # 材料
    material = ConstantMaterial("air", c=1.0)

    # 源项
    mu0 = 4e-7 * np.pi
    current_density = 1e6

    def source_func(x, y, z):
        if (x-0.5)**2 + (y-0.5)**2 < 0.1**2:
            return mu0 * current_density
        return 0.0

    # 组装
    assembler = Assembler(solver_mesh)
    A, M, b = assembler.assemble(material, source_func)

    # ===============================
    # 🔥 边界条件（全自动）
    # ===============================
    bc_manager = BCManager()

    boundary_nodes = find_boundary_nodes(solver_mesh)

    for nid in boundary_nodes:
        bc_manager.add_dirichlet_node(nid, 0.0)

    # ⭐ pin node（防奇异）
    bc_manager.add_dirichlet_node(0, 0.0)

    A, b = bc_manager.apply_all(A, b, solver_mesh)

    # ===============================
    # 诊断
    # ===============================
    diag = FEMDiagnostics(solver_mesh, A, b)
    diag.run_all()

    # 求解
    solver = DirectSolver()
    Az = solver.solve(A, b)

    print("求解完成")