class VTKWriter:
    @staticmethod
    def write(mesh, solution, filename="solution.vtk"):
        with open(filename, 'w') as f:
            f.write("# vtk DataFile Version 3.0\n")
            f.write("FEM Solution\n")
            f.write("ASCII\n")
            f.write("DATASET UNSTRUCTURED_GRID\n")
            f.write(f"POINTS {mesh.node_count} float\n")
            for node in mesh.nodes:
                f.write(f"{node.x} {node.y} {node.z}\n")
            
            triangles = [e for e in mesh.elements if len(e.nodes) == 3]
            tetrahedra = [e for e in mesh.elements if len(e.nodes) == 4]
            total_cells = len(triangles) + len(tetrahedra)
            total_ints = sum(4 for _ in triangles) + sum(5 for _ in tetrahedra)
            f.write(f"CELLS {total_cells} {total_ints}\n")
            for elem in triangles:
                n0, n1, n2 = [n.id for n in elem.nodes]
                f.write(f"3 {n0} {n1} {n2}\n")
            for elem in tetrahedra:
                n0, n1, n2, n3 = [n.id for n in elem.nodes]
                f.write(f"4 {n0} {n1} {n2} {n3}\n")
            
            f.write(f"CELL_TYPES {total_cells}\n")
            for _ in triangles:
                f.write("5\n")
            for _ in tetrahedra:
                f.write("10\n")
            
            f.write(f"POINT_DATA {mesh.node_count}\n")
            f.write("SCALARS solution float 1\n")
            f.write("LOOKUP_TABLE default\n")
            # ✅ 【正确】按节点ID顺序输出！！！
            for node in mesh.nodes:
                f.write(f"{solution[node.id]}\n")

class TextWriter:
    @staticmethod
    def write(mesh, solution, filename="solution.txt"):
        with open(filename, 'w') as f:
            f.write("# id    x        y        z        u\n")
            for node, val in zip(mesh.nodes, solution):
                f.write(f"{node.id:4d} {node.x:8.6f} {node.y:8.6f} {node.z:8.6f} {val:12.8f}\n")
