def parse_gauss_jordan_elimination(text: str):
    """
    Parse a system of linear equations given as text into an augmented matrix and list of variables.
    Assumes each equation is in the form "ax+by+cz=number", variables are single letters, and no spaces.
    Returns:
        - matrix: List of lists representing the augmented matrix [A|B]
        - variables: List of variable names in the order they appear
    """
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

            coef_str = ""
            while i < len(left) and left[i].isdigit():
                coef_str += left[i]
                i += 1

            coef = int(coef_str) if coef_str else 1
            var = left[i]
            i += 1

            if var not in variables:
                variables.append(var)

            equation[var] = equation.get(var, 0) + sign * coef

        equation["const"] = int(right)
        equations.append(equation)

    matrix = []
    for eq in equations:
        row = [eq.get(v, 0) for v in variables]
        row.append(eq["const"])
        matrix.append(row)

    return matrix, variables


def gauss_jordan_elimination(aug_matrix):
    """
    Perform Gauss-Jordan elimination on an augmented matrix [A|B] or on equations given as text.
    Returns a descriptive string containing:
        - The RREF of the augmented matrix
        - The nature of the solution: unique with values, infinite, or no solution
    """
    # If input is not a list of lists, treat it as equation text
    if not isinstance(aug_matrix, list):
        aug_matrix, variables = parse_gauss_jordan_elimination(aug_matrix)
    else:
        variables = [f"x{i+1}" for i in range(len(aug_matrix[0]) - 1)]

    # Convert to float for pivot operations
    M = [list(map(float, row)) for row in aug_matrix]
    N = len(M)
    cols = len(M[0])
    lead = 0

    for r in range(N):
        if lead >= cols - 1:
            break

        i = r
        while i < N and abs(M[i][lead]) < 1e-12:
            i += 1

        if i == N:
            lead += 1
            continue

        # Swap rows r and i
        M[r], M[i] = M[i], M[r]
        pivot = M[r][lead]
        M[r] = [x / pivot for x in M[r]]  # Normalize pivot row

        for j in range(N):
            if j != r:
                factor = M[j][lead]
                M[j] = [m_j - factor * m_r for m_j, m_r in zip(M[j], M[r])]

        lead += 1

    # Check for inconsistency: 0 = nonzero
    for row in M:
        if all(abs(x) < 1e-12 for x in row[:-1]) and abs(row[-1]) > 1e-12:
            rref_str = "\n".join(
                ["[" + ", ".join(f"{val:.3f}" for val in row) + "]" for row in M]
            )
            return (
                "RREF of augmented matrix:\n"
                f"{rref_str}\n\n"
                "Result: The system is inconsistent (no solution)."
            )

    # Count pivot rows
    pivot_rows = sum(1 for row in M if any(abs(x) > 1e-12 for x in row[:-1]))
    if pivot_rows < cols - 1:
        rref_str = "\n".join(
            ["[" + ", ".join(f"{val:.3f}" for val in row) + "]" for row in M]
        )
        return (
            "RREF of augmented matrix:\n"
            f"{rref_str}\n\n"
            "Result: The system has infinitely many solutions."
        )

    # Unique solution: extract values
    solution = {}
    for i, row in enumerate(M):
        for j in range(cols - 1):
            if abs(row[j] - 1) < 1e-12:
                solution[variables[j]] = row[-1]
                break

    rref_str = "\n".join(
        ["[" + ", ".join(f"{val:.3f}" for val in row) + "]" for row in M]
    )
    sol_str = ", ".join(f"{var} = {value:.3f}" for var, value in solution.items())

    return (
        "RREF of augmented matrix:\n"
        f"{rref_str}\n\n"
        f"Result: Unique solution → {sol_str}"
    )


def determinant(A, tol=1e-12):
    """
    Compute the determinant of a square matrix A using LU decomposition (partial pivoting).
    Returns a descriptive string with the determinant value.
    """
    n = len(A)
    if any(len(row) != n for row in A):
        return "Error: Determinant is defined only for square matrices."

    # Make a working copy
    M = [list(map(float, row)) for row in A]
    det = 1.0

    for i in range(n):
        # Find pivot row
        pivot_row = max(range(i, n), key=lambda r: abs(M[r][i]))
        if abs(M[pivot_row][i]) < tol:
            return "Determinant: 0.0 (matrix is singular)"
        if pivot_row != i:
            M[i], M[pivot_row] = M[pivot_row], M[i]
            det *= -1.0

        pivot = M[i][i]
        det *= pivot
        for r in range(i + 1, n):
            factor = M[r][i] / pivot
            for c in range(i, n):
                M[r][c] -= factor * M[i][c]

    return f"Determinant: {det:.6f}"


def inverse(A, tol=1e-12):
    """
    Compute the inverse of a square matrix A using Gauss-Jordan elimination.
    Returns a descriptive string: either the inverse matrix or a message if singular.
    """
    n = len(A)
    if any(len(row) != n for row in A):
        return "Error: Inverse is defined only for square matrices."

    # Create copies for manipulation
    M = [list(map(float, row)) for row in A]
    inv = [[float(i == j) for j in range(n)] for i in range(n)]

    for i in range(n):
        # Find pivot row
        pivot_row = max(range(i, n), key=lambda r: abs(M[r][i]))
        if abs(M[pivot_row][i]) < tol:
            return "Inverse: Matrix is singular (no inverse)."
        if pivot_row != i:
            M[i], M[pivot_row] = M[pivot_row], M[i]
            inv[i], inv[pivot_row] = inv[pivot_row], inv[i]

        pivot = M[i][i]
        M[i] = [x / pivot for x in M[i]]
        inv[i] = [x / pivot for x in inv[i]]

        for r in range(n):
            if r != i:
                factor = M[r][i]
                M[r] = [m_r - factor * m_i for m_r, m_i in zip(M[r], M[i])]
                inv[r] = [v_r - factor * v_i for v_r, v_i in zip(inv[r], inv[i])]

    # Format the inverse matrix for display
    inv_str_lines = []
    for row in inv:
        row_str = "[" + ", ".join(f"{val:.6f}" for val in row) + "]"
        inv_str_lines.append(row_str)
    inv_str = "\n".join(inv_str_lines)

    return "Inverse matrix:\n" + inv_str
