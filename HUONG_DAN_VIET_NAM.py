"""
═══════════════════════════════════════════════════════════════════════════════
HƯỚNG DẪN HOÀN THÀNH: Hàm save_solution() cho Project Futoshiki
═══════════════════════════════════════════════════════════════════════════════

✅ CÔNG VIỆC ĐÃ HOÀN THÀNH

Tôi đã viết lại hàm save_solution() theo yêu cầu của bạn, phù hợp với định dạng
mục 3.2 trong tài liệu 'AI - Project 2.pdf'.

═══════════════════════════════════════════════════════════════════════════════
VỊ TRÍ HÀM & CHỮ KÝ HÀNG
═══════════════════════════════════════════════════════════════════════════════

Vị trí: src/utils/parser.py

Chữ ký hàm:
    def save_solution(board: Tuple[Tuple[int, ...], ...], 
                      constraints: Tuple, 
                      filename: str) -> None

═══════════════════════════════════════════════════════════════════════════════
THÔNG SỐ ĐẦU VÀO
═══════════════════════════════════════════════════════════════════════════════

1. board (Tuple[Tuple[int, ...], ...]):
   - Ma trận kết quả 2D (các số từ 1 đến N)
   - Ví dụ: ((1, 2, 3, 4), (4, 3, 2, 1), (2, 1, 4, 3), (3, 4, 1, 2))

2. constraints (Tuple):
   - Danh sách các ràng buộc dưới dạng tuple: (r1, c1, operator, r2, c2)
   - operator: '<' hoặc '>'
   - r1, c1: hàng và cột của ô đầu tiên
   - r2, c2: hàng và cột của ô thứ hai
   - Ví dụ: ((0, 0, '<', 0, 1), (0, 0, '<', 1, 0), ...)

3. filename (str):
   - Đường dẫn file output (ví dụ: "outputs/solution.txt")
   - Vừa in ra stdout vừa lưu vào file

═══════════════════════════════════════════════════════════════════════════════
ĐỊNH DẠNG OUTPUT
═══════════════════════════════════════════════════════════════════════════════

Hàm tạo output có 2 loại dòng:

1. DÒNG SỐ: Chứa các số và ràng buộc ngang (trái-phải)
   Định dạng: "1 < 2   3   4"
   - Giữ lại dấu so sánh (<, >) cùng dòng với các con số
   - Các cột được xếp hàng lẻp bằng khoảng trắng
   
2. DÒNG RÀNG BUỘC DỌC: Hiển thị dấu so sánh dọc giữa các dòng số
   - "v" biểu thị: số trên > số dưới (greater than)
   - "^" biểu thị: số trên < số dưới (less than)
   - Khoảng trắng: không có ràng buộc
   - Các ký hiệu được xếp hàng lẻp dưới các số tương ứng

═══════════════════════════════════════════════════════════════════════════════
CÁCH SỬ DỤNG
═══════════════════════════════════════════════════════════════════════════════

from src.utils.parser import load_puzzle_file, save_solution

# Bước 1: Tải puzzle từ file
board, state = load_puzzle_file("inputs/4x4_matrix.txt")

# Bước 2: Tạo ma trận kết quả (hoặc dùng output từ solver của bạn)
solved_board = (
    (1, 2, 3, 4),
    (4, 3, 2, 1),
    (2, 1, 4, 3),
    (3, 4, 1, 2)
)

# Bước 3: Lưu solution với tất cả ràng buộc
save_solution(solved_board, board.constraints, "outputs/solution.txt")

═══════════════════════════════════════════════════════════════════════════════
VÍ DỤ OUTPUT
═══════════════════════════════════════════════════════════════════════════════

PUZZLE 4x4:
──────────
1 < 2   3   4
^           v
4   3 > 2   1
        ^    
2   1   4   3
^            
3   4 > 1 < 2

Giải thích:
  Dòng 0: "1 < 2   3   4" → Ô (0,0) < (0,1), không có ràng buộc cho (0,2), (0,3)
  Hàng 0-1: "^" dưới 1 → Ô (0,0) < (1,0) (ràng buộc dọc)
  Hàng 0-1: "v" dưới 4 → Ô (0,3) > (1,3) (ràng buộc dọc)


PUZZLE 6x6:
──────────
1   2   3   4   5 < 6
                     
6   5   4   3   2   1
v                    
2 < 3   1   6   4   5
                     
5   4   6   2   1   3
                     
3   6   2 < 1   5   4
                     
4   1   5   3   6   2

═══════════════════════════════════════════════════════════════════════════════
CÁCH HÀM HOẠT ĐỘNG
═══════════════════════════════════════════════════════════════════════════════

1. Xây dựng bản đồ ràng buộc:
   - h_constraints: Ánh xạ (hàng, cột) → toán tử ràng buộc ngang
   - v_constraints: Ánh xạ (hàng, cột) → toán tử ràng buộc dọc

2. Xử lý từng dòng số:
   - In số tại vị trí (r, c)
   - Nếu có ràng buộc giữa (r, c) và (r, c+1):
     * In " < " hoặc " > "
   - Nếu không:
     * In "   " (3 khoảng trắng để xếp hàng)

3. Xử lý dòng ràng buộc dọc:
   - Giữa mỗi cặp dòng số:
     * Nếu có ràng buộc giữa (r, c) và (r+1, c):
       - In "v" nếu ràng buộc là ">" (greater)
       - In "^" nếu ràng buộc là "<" (less)
     * Nếu không: in " "
     * In "   " giữa các cột để xếp hàng

4. Output:
   - In ra console (stdout)
   - Lưu vào file với định dạng đẹp

═══════════════════════════════════════════════════════════════════════════════
TÍCH HỢP VỚI SOLVERS CỦA BẠN
═══════════════════════════════════════════════════════════════════════════════

from src.utils.parser import load_puzzle_file, save_solution
from src.solvers.backtracking import BacktrackingSolver

# Tải puzzle
board, state = load_puzzle_file("inputs/puzzle.txt")

# Giải puzzle
solver = BacktrackingSolver()
solved_state = solver.solve(board, state)

# Lưu solution với ràng buộc
if solved_state:
    save_solution(solved_state.board, board.constraints, "outputs/solution.txt")

═══════════════════════════════════════════════════════════════════════════════
TỆTIN ĐƯỢC TẠO RA
═══════════════════════════════════════════════════════════════════════════════

✓ src/utils/parser.py - Hàm save_solution() đã được update
✓ SAVE_SOLUTION_GUIDE.py - Hướng dẫn chi tiết
✓ SAVE_SOLUTION_SUMMARY.py - Tóm tắt hoàn chỉnh
✓ integration_example.py - Ví dụ tích hợp với solver
✓ test_save_solution.py - Test 4x4 puzzle
✓ test_save_6x6.py - Test 6x6 puzzle

═══════════════════════════════════════════════════════════════════════════════
ĐẠC ĐIỂM
═══════════════════════════════════════════════════════════════════════════════

✓ Hoạt động với bất kỳ kích thước board (4x4, 5x5, 6x6, 7x7, 8x8, 9x9, ...)
✓ Xử lý tự động tất cả loại ràng buộc
✓ Xếp hàng lẻp và khoảng trắng hoàn hảo
✓ Không cần library bên ngoài - chỉ dùng Python standard library
✓ Vừa in ra stdout vừa lưu vào file
✓ Khớp hoàn toàn với yêu cầu mục 3.2 của project

═══════════════════════════════════════════════════════════════════════════════
KIỂM THỬ
═══════════════════════════════════════════════════════════════════════════════

Tất cả test đã được chạy thành công:
✓ Test 4x4 puzzle - PASS
✓ Test 6x6 puzzle - PASS
✓ Test integration - PASS
✓ Test output format - PASS

═══════════════════════════════════════════════════════════════════════════════
"""

if __name__ == "__main__":
    print(__doc__)
