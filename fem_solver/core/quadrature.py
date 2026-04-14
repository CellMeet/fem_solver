"""数值积分规则"""

class Quadrature:
    """高斯积分规则"""
    
    @staticmethod
    def get_1d_gauss_points(order):
        """获取一维高斯积分点和权重"""
        if order == 1:
            return [(0.0, 2.0)]
        elif order == 2:
            w = 1.0
            x = [-1/math.sqrt(3), 1/math.sqrt(3)]
            return [(x[0], w), (x[1], w)]
        elif order == 3:
            x = [-math.sqrt(3/5), 0.0, math.sqrt(3/5)]
            w = [5/9, 8/9, 5/9]
            return [(x[i], w[i]) for i in range(3)]
        else:
            raise ValueError(f"不支持的高斯积分阶数: {order}")
    
    @staticmethod
    def get_2d_triangle_points(order):
        """
        获取三角形单元的高斯积分点和权重
        使用面积坐标
        """
        if order == 1:
            # 一点积分（中心点）
            return [((1/3, 1/3), 0.5)]
        elif order == 2:
            # 三点积分
            points = [
                ((0.5, 0.5), 1/6),
                ((0.5, 0.0), 1/6),
                ((0.0, 0.5), 1/6)
            ]
            return points
        elif order == 3:
            # 四点积分
            a = 0.6
            b = 0.2
            points = [
                ((1/3, 1/3), -27/96),
                ((a, b), 25/96),
                ((b, a), 25/96),
                ((b, b), 25/96)
            ]
            return points
        else:
            raise ValueError(f"不支持的三角形积分阶数: {order}")