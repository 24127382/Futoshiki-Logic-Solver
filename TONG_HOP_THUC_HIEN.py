╔════════════════════════════════════════════════════════════════════════════════╗
║                                                                                ║
║            HOÀN THÀNH: Hàm save_solution() cho Futoshiki Solver                ║
║                                                                                ║
╚════════════════════════════════════════════════════════════════════════════════╝


✅ TỔNG HỢP CÔNG VIỆC ĐÃ HOÀN THÀNH
═══════════════════════════════════════════════════════════════════════════════

1. ✓ Viết lại hàm save_solution() trong src/utils/parser.py
2. ✓ Hỗ trợ định dạng output theo mục 3.2 (AI Project 2)
3. ✓ In ra stdout + lưu vào file
4. ✓ Xử lý ràng buộc ngang và dọc tự động
5. ✓ Tạo nhiều tệp hướng dẫn và ví dụ
6. ✓ Kiểm thử với 4x4, 6x6 puzzles


═══════════════════════════════════════════════════════════════════════════════
📁 TỆPIN ĐƯỢC TẠO/CẬP NHẬT
═══════════════════════════════════════════════════════════════════════════════

1. [CẬP NHẬT] src/utils/parser.py
   └─ Hàm save_solution() được rewrite hoàn toàn
   └─ Hỗ trợ 3 parameters: board, constraints, filename
   └─ Output format với dấu < > v ^

2. [MỚI] SAVE_SOLUTION_GUIDE.py
   └─ Hướng dẫn chi tiết cách sử dụng
   └─ Ví dụ với các kích thước puzzle khác nhau

3. [MỚI] SAVE_SOLUTION_SUMMARY.py
   └─ Tóm tắt hoàn chỉnh toàn bộ triển khai
   └─ Giải thích cách hàm hoạt động

4. [MỚI] HUONG_DAN_VIET_NAM.py
   └─ Hướng dẫn tiếng Việt
   └─ Phù hợp cho project của bạn

5. [MỚI] integration_example.py
   └─ Ví dụ tích hợp với solver
   └─ Template sẵn sàng sử dụng

6. [MỚI] test_save_solution.py
   └─ Test case 4x4 puzzle

7. [MỚI] test_save_6x6.py
   └─ Test case 6x6 puzzle


═══════════════════════════════════════════════════════════════════════════════
🎯 CHỮÍN HÀNG - Hàm save_solution()
═══════════════════════════════════════════════════════════════════════════════

def save_solution(board: Tuple[Tuple[int, ...], ...], 
                  constraints: Tuple, 
                  filename: str) -> None

PARAMETERS:
───────────

• board (Tuple[Tuple[int, ...], ...])
  Ma trận kết quả 2D giải Futoshiki
  Ví dụ: ((1, 2, 3, 4), (4, 3, 2, 1), ...)

• constraints (Tuple)
  Danh sách ràng buộc: ((r1, c1, op, r2, c2), ...)
  op: '<' hoặc '>'
  Ví dụ: ((0, 0, '<', 0, 1), (0, 0, '<', 1, 0), ...)

• filename (str)
  Đường dẫn file output
  Ví dụ: "outputs/solution.txt"

BEHAVIOR:
─────────

✓ In kết quả có format đẹp ra console (stdout)
✓ Lưu kết quả vào file
✓ Output format:
  - Dòng số với ràng buộc ngang: "1 < 2   3   4"
  - Dòng ràng buộc dọc: "^   v"


═══════════════════════════════════════════════════════════════════════════════
📋 ĐỊNH DẠNG OUTPUT CHI TIẾT
═══════════════════════════════════════════════════════════════════════════════

DÒNG SỐ (Number rows):
──────────────────────
Format: "số operator số operator số ..."
Ví dụ:  "1 < 2   3   4"
        "4   3 > 2   1"

• Số được in lập tức
• Nếu có ràng buộc giữa (r,c) và (r,c+1): in " < " hoặc " > "
• Nếu không: in "   " (3 khoảng trắng để xếp hàng)


DÒNG RÀNG BUỘC DỌC (Constraint rows):
────────────────────────────────────────
Hiển thị giữa các dòng số
Format: "symbol   symbol   symbol"
Ví dụ:  "^           v"
        "        ^    "

• "v" = số trên > số dưới (top > bottom)
• "^" = số trên < số dưới (top < bottom)
• " " = không có ràng buộc
• Xếp hàng lẻp dưới các số tương ứng


═══════════════════════════════════════════════════════════════════════════════
💻 CÁCH SỬ DỤNG - QUICK START
═══════════════════════════════════════════════════════════════════════════════

from src.utils.parser import load_puzzle_file, save_solution

# 1. Load puzzle
board, state = load_puzzle_file("inputs/4x4_matrix.txt")

# 2. Tạo ma trận kết quả (hoặc dùng output từ solver)
solved_board = (
    (1, 2, 3, 4),
    (4, 3, 2, 1),
    (2, 1, 4, 3),
    (3, 4, 1, 2)
)

# 3. Lưu solution
save_solution(solved_board, board.constraints, "outputs/solution.txt")


═══════════════════════════════════════════════════════════════════════════════
📊 OUTPUT VÍ DỤ
═══════════════════════════════════════════════════════════════════════════════

INPUT: 4x4 puzzle với constraints
OUTPUT:

1 < 2   3   4
^           v
4   3 > 2   1
        ^    
2   1   4   3
^            
3   4 > 1 < 2

GIẢI THÍCH:
───────────
Dòng 0: "1 < 2   3   4"
  ├─ (0,0)=1, (0,1)=2 với ràng buộc 1 < 2 ✓
  ├─ (0,2)=3 không có ràng buộc với (0,1)
  └─ (0,3)=4 không có ràng buộc với (0,2)

Dòng 1 (ràng buộc dọc):
  ├─ "^" dưới 1: (0,0) < (1,0) ✓
  ├─ " " dưới 2: không có ràng buộc
  ├─ " " dưới 3: không có ràng buộc
  └─ "v" dưới 4: (0,3) > (1,3) ✓

Dòng 2: "4   3 > 2   1"
  ├─ (1,0)=4
  ├─ (1,1)=3, (1,2)=2 với ràng buộc 3 > 2 ✓
  └─ (1,3)=1

... và cứ tiếp tục như vậy


═══════════════════════════════════════════════════════════════════════════════
🧪 KIỂM THỬ
═══════════════════════════════════════════════════════════════════════════════

Tất cả test đã được chạy thành công:

✓ test_save_solution.py (4x4)
  └─ Load puzzle từ file
  └─ Tạo solved board
  └─ Save solution với constraints
  └─ Kết quả output chính xác

✓ test_save_6x6.py (6x6)
  └─ Test với puzzle lớn hơn
  └─ Verify spacing và alignment

✓ integration_example.py
  └─ Demo workflow hoàn chỉnh
  └─ Xử lý 4x4 và 6x6 puzzles
  └─ Output file được tạo đúng


═══════════════════════════════════════════════════════════════════════════════
🔄 TÍCH HỢP VỚI SOLVER CỦA BẠN
═══════════════════════════════════════════════════════════════════════════════

from src.utils.parser import load_puzzle_file, save_solution
from src.solvers.backtracking import BacktrackingSolver  # Hoặc solver khác

def main():
    # Load puzzle
    board, state = load_puzzle_file("inputs/puzzle.txt")
    
    # Solve
    solver = BacktrackingSolver()
    solved_state = solver.solve(board, state)
    
    # Save with constraints
    if solved_state:
        save_solution(
            solved_state.board,
            board.constraints,
            "outputs/solution.txt"
        )
        print("✓ Solution saved!")
    else:
        print("✗ No solution found")

if __name__ == "__main__":
    main()


═══════════════════════════════════════════════════════════════════════════════
🌟 TÍNH NĂNG ĐẶC BIỆT
═══════════════════════════════════════════════════════════════════════════════

✓ Hoạt động với bất kỳ kích thước (4x4, 5x5, 6x6, 7x7, 8x8, 9x9, ...)
✓ Tự động xây dựng constraint maps
✓ Xếp hàng lẻp tự động
✓ Không cần tính toán khoảng trắng thủ công
✓ Output chuẩn và đẹp
✓ Chỉ dùng Python standard library (không dependency)
✓ Vừa in ra stdout vừa lưu file
✓ Khớp yêu cầu mục 3.2 của project


═══════════════════════════════════════════════════════════════════════════════
📚 TỆPIN HƯỚNG DẪN
═══════════════════════════════════════════════════════════════════════════════

Để hiểu chi tiết hơn, đọc các file:

1. SAVE_SOLUTION_GUIDE.py - Hướng dẫn chi tiết
2. SAVE_SOLUTION_SUMMARY.py - Tóm tắt toàn bộ
3. HUONG_DAN_VIET_NAM.py - Hướng dẫn tiếng Việt
4. integration_example.py - Ví dụ tích hợp


═══════════════════════════════════════════════════════════════════════════════
✨ KẾT LUẬN
═══════════════════════════════════════════════════════════════════════════════

Hàm save_solution() đã sẵn sàng sử dụng ngay trong project của bạn.

Công dụng:
  • Save solution đã giải với tất cả ràng buộc
  • Output format chuẩn theo tài liệu project
  • Sử dụng dễ dàng, chỉ cần gọi 1 dòng code
  • Có thể tích hợp với bất kỳ solver nào

Chúc bạn thành công! 🎉

═══════════════════════════════════════════════════════════════════════════════
"""

if __name__ == "__main__":
    print(__doc__)
