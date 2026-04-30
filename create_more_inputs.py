import os

def create_puzzle(filename, size, grid, h_constraints, v_constraints):
    content = f"{size}\n\n"
    for row in grid:
        content += ", ".join(map(str, row)) + "\n"
    content += "\n"
    for row in h_constraints:
        content += ", ".join(map(str, row)) + "\n"
    content += "\n"
    for row in v_constraints:
        content += ", ".join(map(str, row)) + "\n"
    
    with open(f"inputs/{filename}", "w") as f:
        f.write(content)

# 6x6 Puzzle
create_puzzle("6x6_matrix.txt", 6,
    [[0]*6 for _ in range(6)],
    [[0]*5 for _ in range(6)],
    [[0]*6 for _ in range(5)]
)

# 8x8 Puzzle
create_puzzle("8x8_matrix.txt", 8,
    [[0]*8 for _ in range(8)],
    [[0]*7 for _ in range(8)],
    [[0]*8 for _ in range(7)]
)

# 9x9 Puzzle
create_puzzle("9x9_matrix.txt", 9,
    [[0]*9 for _ in range(9)],
    [[0]*8 for _ in range(9)],
    [[0]*9 for _ in range(8)]
)

# Hard 4x4
create_puzzle("4x4_hard.txt", 4,
    [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
    [[1, 0, -1], [0, 0, 0], [0, 1, 0], [-1, 0, 0]],
    [[0, 1, 0, 0], [0, 0, -1, 0], [1, 0, 0, 0]]
)

# Hard 5x5
create_puzzle("5x5_hard.txt", 5,
    [[0]*5 for _ in range(5)],
    [[1, 0, 0, -1], [0, 1, 0, 0], [0, 0, -1, 0], [1, 0, 0, 0], [0, -1, 0, 0]],
    [[0, 1, 0, 0, 0], [0, 0, -1, 0, 1], [1, 0, 0, 0, 0], [0, 0, 0, -1, 0]]
)

# Hard 6x6
create_puzzle("6x6_hard.txt", 6,
    [[0]*6 for _ in range(6)],
    [[1, 0, 0, 0, -1], [0, 0, 0, 0, 0], [0, 1, 0, -1, 0], [0, 0, 0, 0, 0], [1, 0, -1, 0, 0], [0, 0, 0, 0, 0]],
    [[0]*6 for _ in range(5)]
)

print("Created additional puzzles in inputs/")
