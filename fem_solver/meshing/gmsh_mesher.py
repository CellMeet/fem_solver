# fem_solver/meshing/gmsh_mesher.py
import gmsh
import meshio
import numpy as np
from fem_solver.core.mesh import Mesh
from fem_solver.core.node import Node
from fem_solver.core.element import TetrahedronElement

class GmshMesher:
    @staticmethod
    def create_box_mesh(xmin, xmax, ymin, ymax, zmin, zmax, mesh_size=0.05, filename="box.msh"):
        gmsh.initialize()
        gmsh.model.add("box")

        # 优化网格
        gmsh.option.setNumber("Mesh.CharacteristicLengthMin", mesh_size)
        gmsh.option.setNumber("Mesh.CharacteristicLengthMax", mesh_size)
        gmsh.option.setNumber("Mesh.Algorithm3D", 10)
        gmsh.option.setNumber("Mesh.Optimize", 1)
        gmsh.option.setNumber("Mesh.OptimizeNetgen", 1)

        gmsh.model.occ.addBox(xmin, ymin, zmin, xmax-xmin, ymax-ymin, zmax-zmin)
        gmsh.model.occ.synchronize()
        

        
        gmsh.model.mesh.generate(3)
        gmsh.write(filename)
        gmsh.finalize()
        return filename

    @staticmethod
    def load_mesh(filename):
        meshio_mesh = meshio.read(filename)
        points = meshio_mesh.points

        # 提取四面体单元
        tetra_cells = None
        for cell in meshio_mesh.cells:
            if cell.type == "tetra":
                tetra_cells = cell.data
                break

        if tetra_cells is None:
            raise ValueError("No tetrahedral cells found in mesh")

        solver_mesh = Mesh()

        # 读取节点
        for i, (x, y, z) in enumerate(points):
            solver_mesh.nodes.append(Node(i, x, y, z))
        solver_mesh.node_count = len(points)

        # 读取单元（✅ 1-based → 0-based，缩进完全正确）
        for eid, cell_data in enumerate(tetra_cells):
            n0, n1, n2, n3 = cell_data
            nodes = [
                solver_mesh.nodes[n0],
                solver_mesh.nodes[n1],
                solver_mesh.nodes[n2],
                solver_mesh.nodes[n3]
            ]
            elem = TetrahedronElement(eid, nodes)
            solver_mesh.elements.append(elem)

        solver_mesh.element_count = len(tetra_cells)

        print("===== meshio 索引检查 =====")
        print("tetra_cells 前5个:")
        print(tetra_cells[:5])

        print("最小索引:", tetra_cells.min())
        print("最大索引:", tetra_cells.max())
        print("节点总数:", len(points))
        return solver_mesh
