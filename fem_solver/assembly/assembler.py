from collections import defaultdict
import numpy as np

class Assembler:
    def __init__(self, mesh):
        self.mesh = mesh
        self.n_nodes = mesh.node_count
        self.A = defaultdict(float)

    def assemble(self, material, source_func):
        self.A.clear()
        b = np.zeros(self.n_nodes)

        for elem in self.mesh.elements:

            # ❗只保留四面体
            if len(elem.nodes) != 4:
                continue
            
            # 调用我们刚刚修好的、稳健的单元计算
            Ke = elem.compute_stiffness_matrix(material)
            fe = elem.compute_load_vector(source_func)
            ids = [n.id for n in elem.nodes]

            for i, gi in enumerate(ids):
                b[gi] += fe[i]
                for j, gj in enumerate(ids):
                    self.A[(gi, gj)] += Ke[i, j]

        return self.A, None, b


