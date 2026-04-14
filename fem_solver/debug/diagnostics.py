import numpy as np

class FEMDiagnostics:
    """
    FEM 自动诊断系统（轻量工程版）
    """

    def __init__(self, mesh, A=None, b=None):
        self.mesh = mesh
        self.A = A
        self.b = b

    # =========================
    # 1. Mesh 检查
    # =========================
    def check_mesh_integrity(self):
        print("\n[Mesh Check]")

        total_nodes = len(self.mesh.nodes)
        used_nodes = set()

        for elem in self.mesh.elements:
            for n in elem.nodes:
                used_nodes.add(n.id)

        isolated = set(range(total_nodes)) - used_nodes

        print(f"Total nodes: {total_nodes}")
        print(f"Used nodes: {len(used_nodes)}")
        print(f"Isolated nodes: {len(isolated)}")

        if len(isolated) > 0:
            print("⚠ WARNING: isolated nodes exist!")
            return False

        print("✔ Mesh integrity OK")
        return True

    # =========================
    # 2. 组装完整性检查
    # =========================
    def check_assembly(self):
        print("\n[FEM Assembly Check]")

        if self.A is None:
            print("❌ No stiffness matrix provided")
            return False

        row_count = {}
        for (i, j), v in self.A.items():
            row_count[i] = row_count.get(i, 0) + abs(v)

        zero_rows = [i for i, v in row_count.items() if v == 0]

        print(f"Total DOFs with stiffness: {len(row_count)}")
        print(f"Zero rows: {len(zero_rows)}")

        if len(zero_rows) > 0:
            print("⚠ WARNING: zero stiffness rows detected!")
            return False

        print("✔ Assembly OK")
        return True

    # =========================
    # 3. RHS检查（source）
    # =========================
    def check_rhs(self):
        print("\n[Source Check]")

        if self.b is None:
            print("❌ No RHS vector provided")
            return False

        if isinstance(self.b, dict):
                values = self.b
        else:
                values = self.b

        nonzero = np.sum(np.abs(values) > 1e-14)

        print(f"Non-zero RHS entries: {nonzero}")

        if nonzero == 0:
            print("⚠ WARNING: RHS is all zero!")
            return False

        print("✔ RHS OK")
        return True

    # =========================
    # 4. Dirichlet覆盖检查
    # =========================
    def check_dirichlet_coverage(self):
        print("\n[Dirichlet Check]")

        if self.A is None:
            return False

        constrained = set()

        for (i, j), v in self.A.items():
            # 很大的对角项通常表示Dirichlet
            if i == j and abs(v) > 1e12:
                constrained.add(i)

        print(f"Constrained DOFs: {len(constrained)}")

        if len(constrained) == 0:
            print("⚠ WARNING: no Dirichlet constraints detected!")
            return False

        print("✔ Dirichlet OK")
        return True

    # =========================
    # 5. 数值稳定性检查
    # =========================
    def check_matrix_stability(self):
        print("\n[Numerical Stability]")

        if self.A is None:
            return False

        diag_zeros = 0
        for (i, j), v in self.A.items():
            if i == j and abs(v) < 1e-14:
                diag_zeros += 1

        print(f"Zero diagonal entries: {diag_zeros}")

        if diag_zeros > 0:
            print("⚠ WARNING: zero diagonal detected!")
            return False

        print("✔ Matrix diagonal OK")
        return True

    # =========================
    # 总检查入口
    # =========================
    def run_all(self):
        print("\n============================")
        print("   FEM DIAGNOSTIC REPORT")
        print("============================")

        results = []
        results.append(self.check_mesh_integrity())
        results.append(self.check_assembly())
        results.append(self.check_rhs())
        results.append(self.check_dirichlet_coverage())
        results.append(self.check_matrix_stability())

        print("\n============================")
        if all(results):
            print("✔ SYSTEM STATUS: OK")
        else:
            print("⚠ SYSTEM STATUS: ISSUES DETECTED")
        print("============================\n")