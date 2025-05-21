



def gauss_jordan_elimination(aug_matrix):
    """
    Perform Gauss-Jordan elimination on an augmented matrix [A|B] and return the solutions.

    Args:
        aug_matrix: Combined matrix where the last column represents the right-hand side (B)
                    It can be either a list of lists or a system of equations in text form.

    Returns:
        A dictionary containing:
        - 'rref': The reduced row echelon form of the augmented matrix
        - 'solution': The solution vector (if unique), 'infinite' (if infinitely many), or 'no solution' (if inconsistent)
    """
    if not isinstance(aug_matrix, list):
        aug_matrix, variables = parse_gauss_jordan_elimination(aug_matrix)
    else:
        variables = [f"x{i+1}" for i in range(len(aug_matrix[0]) - 1)]

    N = len(aug_matrix)
    M = len(aug_matrix[0])
    lead = 0

    for r in range(N):
        if lead >= M - 1:
            break

        i = r
        while i < N and aug_matrix[i][lead] == 0:
            i += 1

        if i == N:
            lead += 1
            continue

        aug_matrix[r], aug_matrix[i] = aug_matrix[i], aug_matrix[r]
        pivot = aug_matrix[r][lead]
        aug_matrix[r] = [x / pivot for x in aug_matrix[r]]

        for j in range(N):
            if j != r:
                factor = aug_matrix[j][lead]
                aug_matrix[j] = [
                    elem_j - factor * elem_r
                    for elem_j, elem_r in zip(aug_matrix[j], aug_matrix[r])
                ]
        lead += 1

    # Check for inconsistency
    for row in aug_matrix:
        if all(abs(x) < 1e-9 for x in row[:-1]) and abs(row[-1]) > 1e-9:
            return "no solution"

    # Check for infinite solutions
    pivot_rows = sum(1 for row in aug_matrix if any(abs(x) > 1e-9 for x in row[:-1]))
    if pivot_rows < M - 1:
        return  "infinite"

    solution = [row[-1] for row in aug_matrix]
    return solution


def parse_gauss_jordan_elimination(text: str):
    lines = text.strip().splitlines()
    equations = []
    variables = []

    for line in lines:
        line = line.replace(" ", "")
        left, right = line.split("=")
        equation = {}
        i = 0
        while i < len(left):
            sign = 1
            if left[i] == "+":
                i += 1
            elif left[i] == "-":
                sign = -1
                i += 1

            coef = ""
            while i < len(left) and left[i].isdigit():
                coef += left[i]
                i += 1

            coef = int(coef) if coef else 1
            var = left[i]
            i += 1

            if var not in variables:
                variables.append(var)

            equation[var] = equation.get(var, 0) + sign * coef

        equation["end"] = int(right)
        equations.append(equation)

    matrix = []
    for eq in equations:
        row = [eq.get(var, 0) for var in variables]
        row.append(eq["end"])
        matrix.append(row)

    return matrix, variables

            
                
                
        
    
    
    
    
    
    

def determinant(A, tol=1e-12):
    n = len(A)
    if any(len(row) != n for row in A):
        raise ValueError("Matrix must be square.")
    M = [row[:] for row in A]
    det = 1.0
    for i in range(n):
        pivot_row = max(range(i, n), key=lambda r: abs(M[r][i]))
        if abs(M[pivot_row][i]) < tol:
            return 0.0
        if pivot_row != i:
            M[i], M[pivot_row] = M[pivot_row], M[i]
            det *= -1
        pivot = M[i][i]
        det *= pivot
        for r in range(i + 1, n):
            factor = M[r][i] / pivot
            for c in range(i, n):
                M[r][c] -= factor * M[i][c]
    return det


def inverse(A, tol=1e-12):
    n = len(A)
    if any(len(row) != n for row in A):
        raise ValueError("Matrix must be square.")
    M = [row[:] for row in A]
    inv = [[float(i == j) for j in range(n)] for i in range(n)]
    for i in range(n):
        pivot_row = max(range(i, n), key=lambda r: abs(M[r][i]))
        if abs(M[pivot_row][i]) < tol:
            return None
        if pivot_row != i:
            M[i], M[pivot_row] = M[pivot_row], M[i]
            inv[i], inv[pivot_row] = inv[pivot_row], inv[i]
        piv = M[i][i]
        M[i] = [v / piv for v in M[i]]
        inv[i] = [v / piv for v in inv[i]]
        for r in range(n):
            if r != i:
                factor = M[r][i]
                M[r] = [v_r - factor * v_p for v_r, v_p in zip(M[r], M[i])]
                inv[r] = [u_r - factor * u_p for u_r, u_p in zip(inv[r], inv[i])]
    return inv




import unittest

class TestMatrixOperations(unittest.TestCase):

    def test_determinant_identity(self):
        I = [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0]
        ]
        self.assertAlmostEqual(determinant(I), 1.0)

    def test_determinant_zero(self):
        A = [
            [1.0, 2.0, 3.0],
            [4.0, 5.0, 6.0], 
            [7.0, 8.0, 9.0]
        ]
        self.assertAlmostEqual(determinant(A), 0.0)

    def test_determinant_known(self):
        A = [
            [2, 5, 3],
            [1, -2, -1],
            [1, 3, 4]
        ]
        self.assertAlmostEqual(determinant(A), -20.0)

    def test_inverse_identity(self):
        I = [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0]
        ]
        invI = inverse(I)
        self.assertIsNotNone(invI)
        for i in range(3):
            for j in range(3):
                self.assertAlmostEqual(invI[i][j], I[i][j])

    def test_inverse_known(self):
        A = [
            [4.0, 7.0],
            [2.0, 6.0]
        ]
        inv_expected = [
            [0.6, -0.7],
            [-0.2, 0.4]
        ]
        invA = inverse(A)
        self.assertIsNotNone(invA)
        for i in range(2):
            for j in range(2):
                self.assertAlmostEqual(invA[i][j], inv_expected[i][j], places=7)

    def test_inverse_singular(self):
        A = [
            [1, 2],
            [2, 4]
        ]
        self.assertIsNone(inverse(A))


class TestGaussJordanElimination(unittest.TestCase):

    def test_simple_system(self):
        # x + y = 2, x - y = 0
        A = [
            [1.0, 1.0, 2.0],
            [1.0, -1.0, 0.0]
        ]
        result = gauss_jordan_elimination(A)
        self.assertAlmostEqual(result[0], 1.0)
        self.assertAlmostEqual(result[1], 1.0)

    def test_identity_system(self):
        # x = 3, y = 4, z = 5
        A = [
            [1.0, 0.0, 0.0, 3.0],
            [0.0, 1.0, 0.0, 4.0],
            [0.0, 0.0, 1.0, 5.0]
        ]
        result = gauss_jordan_elimination(A)
        self.assertEqual(result, [3.0, 4.0, 5.0])

    def test_singular_system(self):
        A = [
            [1.0, 1.0, 2.0],
            [2.0, 2.0, 4.0]
        ]
        self.assertEqual(
            gauss_jordan_elimination(A), "infinite")


if __name__ == '__main__':
    unittest.main()