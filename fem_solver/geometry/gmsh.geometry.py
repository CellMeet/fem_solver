# fem_solver/meshing/gmsh_geometry.py
import gmsh
import meshio
import numpy as np

class GmshGeometry:
    def __init__(self):
        self.initialized = False

    def _init(self):
        if not self.initialized:
            gmsh.initialize()
            gmsh.option.setNumber("General.Terminal", 1)
            self.initialized = True

    def create_box_mesh(self, xmin=0, xmax=1, ymin=0, ymax=1, zmin=0, zmax=1,
                        mesh_size=0.05, physical_groups=None):
        """
        创建一个长方体，划分四面体网格。
        physical_groups: dict, 例如 {'bottom': (2, [tag]), 'top': (2, [tag]), ...}
                         tag 为面的标签，需要从创建的面中获取。
        """
        self._init()
        gmsh.model.clear()
        gmsh.model.add("Box")

        # 创建长方体
        box = gmsh.model.occ.addBox(xmin, ymin, zmin,
                                    xmax-xmin, ymax-ymin, zmax-zmin)
        gmsh.model.occ.synchronize()

        # 获取所有面（dim=2）
        entities = gmsh.model.getEntities()
        surfaces = {dim: tag for dim, tag in entities if dim == 2}
        # 按照坐标范围识别六个面
        # 注意：tag 是随机分配的，需要根据几何位置确定
        # 这里简单起见，假设知道面的顺序（Gmsh 按创建顺序编号）
        # 更可靠的方法：用 gmsh.model.getBoundary 或通过中心点判断
        # 我们手动标记：底面 z=zmin, 顶面 z=zmax, 等等
        # 为了通用性，使用函数判断
        surface_tags = []
        for dim, tag in entities:
            if dim == 2:
                surface_tags.append(tag)
        # 计算每个面的中心点
        centers = {}
        for tag in surface_tags:
            # 获取该面的所有点
            _, pts, _ = gmsh.model.getBoundary([(2, tag)])
            # 计算中心（近似）
            xs, ys, zs = [], [], []
            for pt in pts:
                coord = gmsh.model.getValue(0, pt[1], [])
                xs.append(coord[0]); ys.append(coord[1]); zs.append(coord[2])
            centers[tag] = (np.mean(xs), np.mean(ys), np.mean(zs))

        # 根据中心点坐标匹配物理组名称
        for tag, (cx, cy, cz) in centers.items():
            if abs(cz - zmin) < 1e-6:
                name = 'bottom'
            elif abs(cz - zmax) < 1e-6:
                name = 'top'
            elif abs(cx - xmin) < 1e-6:
                name = 'left'
            elif abs(cx - xmax) < 1e-6:
                name = 'right'
            elif abs(cy - ymin) < 1e-6:
                name = 'front'
            elif abs(cy - ymax) < 1e-6:
                name = 'back'
            else:
                continue
            gmsh.model.addPhysicalGroup(2, [tag], tag=tag)
            gmsh.model.setPhysicalName(2, tag, name)

        # 添加整个体的物理组（可选）
        gmsh.model.addPhysicalGroup(3, [box], tag=1)
        gmsh.model.setPhysicalName(3, 1, "volume")

        # 设置网格尺寸
        gmsh.option.setNumber("Mesh.CharacteristicLengthMin", mesh_size)
        gmsh.option.setNumber("Mesh.CharacteristicLengthMax", mesh_size)

        # 生成 3D 网格
        gmsh.model.mesh.generate(3)

        # 保存为 msh 文件
        gmsh.write("box.msh")
        gmsh.finalize()

        # 用 meshio 读取并返回节点和单元
        mesh = meshio.read("box.msh")
        points = mesh.points
        # 提取四面体单元
        cells = mesh.cells
        tetra_cells = None
        for cell_block in cells:
            if cell_block.type == "tetra":
                tetra_cells = cell_block.data
                break
        # 提取表面三角形（用于后处理显示，可选）
        tri_cells = None
        for cell_block in cells:
            if cell_block.type == "triangle":
                tri_cells = cell_block.data
                break

        # 读取物理组标记（边界条件）
        # meshio 中 field_data 存储物理组信息
        physical_groups_info = mesh.field_data  # {"bottom": 2, ...}
        # 需要将物理组 tag 映射到对应的面单元
        # 这里简化：直接从网格中获取每个面的单元标签
        # 实际上需要从 mesh.cell_data 中提取 "gmsh:physical"
        # 略复杂，简单起见，我们手动在 Gmsh 中已经用物理组命名了面，读取时可以按物理组提取面单元
        # 但是为了求解，我们只需要知道哪些节点属于边界条件，可以通过节点坐标判断（因为几何简单）
        return points, tetra_cells, tri_cells, physical_groups_info