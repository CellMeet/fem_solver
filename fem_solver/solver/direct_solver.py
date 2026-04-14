from .linear_solver import LinearSolver
import numpy as np

class DirectSolver(LinearSolver):

    def __init__(self):
        super().__init__("Direct Solver (Gaussian Elimination)")

    def solve(self, A, b):

        n = len(b)

        # -------------------------
        # ✅ 正确：字典 -> dense matrix
        # -------------------------
        A_dense = np.zeros((n, n), dtype=float)

        for (i, j), val in A.items():
            A_dense[i, j] = float(val)

        b_dense = np.array(b, dtype=float)

        # -------------------------
        # 高斯消元
        # -------------------------
        for i in range(n):

            # pivot
            pivot = i
            max_val = abs(A_dense[i, i])

            for k in range(i + 1, n):
                if abs(A_dense[k, i]) > max_val:
                    max_val = abs(A_dense[k, i])
                    pivot = k

            if pivot != i:
                A_dense[[i, pivot]] = A_dense[[pivot, i]]
                b_dense[[i, pivot]] = b_dense[[pivot, i]]

            if abs(A_dense[i, i]) < 1e-14:
                continue

            # elimination
            for k in range(i + 1, n):
                factor = A_dense[k, i] / A_dense[i, i]
                if abs(factor) < 1e-16:
                    continue

                A_dense[k, i:] -= factor * A_dense[i, i:]
                b_dense[k] -= factor * b_dense[i]

        # -------------------------
        # back substitution
        # -------------------------
        u = np.zeros(n, dtype=float)

        for i in range(n - 1, -1, -1):
            u[i] = (b_dense[i] - np.dot(A_dense[i, i+1:], u[i+1:])) / A_dense[i, i]

        return u