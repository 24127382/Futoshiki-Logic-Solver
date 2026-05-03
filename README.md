# Futoshiki Solver - Công cụ giải Futoshiki

<div align="center">

**[🇻🇳 Tiếng Việt](#-tiếng-việt) | [🇬🇧 English](#-english)**

</div>

---

## 🇻🇳 Tiếng Việt

### Giới Thiệu

**Futoshiki Solver** là một công cụ toàn diện để giải các câu đố Futoshiki sử dụng nhiều thuật toán AI khác nhau. Đây là một đồ án học tập được phát triển bởi nhóm sinh viên nhằm áp dụng các kiến thức về lập trình logic, tìm kiếm AI và thiết kế giao diện người dùng.

Futoshiki (不等式, có nghĩa là "bất đẳng thức") là một câu đố logic tương tự như Sudoku. Mục đích là điền các số vào lưới sao cho:
- Mỗi hàng chứa các số từ 1 đến N không lặp lại
- Mỗi cột chứa các số từ 1 đến N không lặp lại
- Tất cả các ràng buộc bất đẳng thức được thỏa mãn

### Yêu Cầu Hệ Thống

- **Python**: >= 3.7 (khuyến nghị >= 3.8)
- **Hệ điều hành**: Windows, macOS, Linux
- **Bộ nhớ**: Tối thiểu 512 MB
- **Ổ cứng**: 500 MB cho các file thư viện (khi cài đặt đầy đủ)

### Cài Đặt

#### 1. Sao chép dự án
```bash
git clone <đường-dẫn-repo>
cd futoshiki-solver
```

#### 2. Tạo và kích hoạt môi trường ảo (Virtual Environment)

**Trên Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Trên macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Cài đặt các thư viện phụ thuộc
```bash
pip install -r requirements.txt
```

Nếu muốn cài đặt thêm các thư viện phát triển (linting, testing, documentation):
```bash
pip install -r requirements-dev.txt
```

### Cấu Trúc Thư Mục

```
futoshiki-solver/
├── src/                         # Mã nguồn chính
│   ├── logic/                   # Xử lý logic và ràng buộc
│   │   ├── axioms.py           # Định nghĩa tiên đề và ràng buộc
│   │   ├── grounding.py        # Tạo các mệnh đề từ quy tắc
│   │   └── logic_utils.py      # Các hàm tiện ích logic
│   ├── models/                  # Cấu trúc dữ liệu
│   │   ├── board.py            # Biểu diễn bảng câu đố
│   │   ├── kb.py               # Cơ sở kiến thức
│   │   └── state.py            # Trạng thái tìm kiếm
│   ├── solvers/                 # Triển khai các thuật toán
│   │   ├── backtracking.py      # Solver backtracking với CSP
│   │   ├── forward_chaining.py  # Lập trình logic tiến
│   │   ├── backward_chaining.py # Lập trình logic lùi
│   │   └── a_star.py            # Tìm kiếm A* với heuristic
│   └── utils/                   # Các hàm hỗ trợ
│       ├── heuristic.py         # Các hàm heuristic
│       └── parser.py            # Phân tích file đầu vào
├── gui/                         # Giao diện người dùng Tkinter
│   ├── app.py                   # Ứng dụng GUI chính
│   ├── board_frame.py           # Hiển thị bảng câu đố
│   ├── sidebar.py               # Thanh điều khiển
│   ├── controller.py            # Controller MVC
│   ├── bridge.py                # Cầu nối định dạng dữ liệu
│   └── README.md                # Tài liệu GUI
├── tests/                       # Bộ kiểm thử
│   ├── test_models.py
│   ├── test_models_advanced.py
│   ├── test_forward_chaining.py
│   ├── test_heuristic.py
│   └── run_tests.py
├── inputs/                      # Các file câu đố mẫu
│   ├── input-01.txt
│   ├── input-02.txt
│   └── ... (tối đa 10 file)
├── outputs/                     # Thư mục lưu kết quả giải
├── main.py                      # Điểm khởi chạy (GUI & CLI)
├── requirements.txt             # Danh sách thư viện phụ thuộc
├── pyproject.toml              # Cấu hình dự án
└── README.md                    # File này
```

### Hướng Dẫn Sử Dụng

#### Cách 1: Chạy Giao Diện GUI (Khuyên dùng)

Chạy lệnh sau để khởi động giao diện đồ họa:
```bash
python main.py
```

Ứng dụng GUI sẽ mở với các tính năng:
- Tải file câu đố từ thư mục `inputs/`
- Chọn thuật toán giải: Backtracking, Forward Chaining, Backward Chaining, A* Search
- Xem kết quả giải trực tiếp trên giao diện
- Lưu kết quả vào thư mục `outputs/`

#### Cách 2: Chạy từ Command Line (CLI)

Giải một câu đố cụ thể bằng thuật toán chỉ định:
```bash
python main.py --cli --input inputs/input-01.txt --solver backtracking --output outputs/
```

**Tham số:**
- `--input`: Đường dẫn file câu đố (bắt buộc)
- `--solver`: Thuật toán sử dụng: `backtracking`, `forward_chaining`, `backward_chaining`, `a_star` (bắt buộc)
- `--output`: Thư mục hoặc file để lưu kết quả (mặc định: `outputs/`)
- `--verbose`: Hiển thị log chi tiết (tùy chọn)

**Ví dụ:**
```bash
# Giải input-01.txt bằng backtracking
python main.py --cli --input inputs/input-01.txt --solver backtracking

# Giải tất cả input bằng A* và lưu vào folder tùy chỉnh
python main.py --cli --input inputs/input-02.txt --solver a_star --output my_outputs/ --verbose
```

#### Cách 3: Chạy Bộ Kiểm Thử

Để kiểm tra toàn bộ giải pháp:
```bash
python tests/run_tests.py
```

Hoặc chạy kiểm thử cụ thể:
```bash
python -m pytest tests/test_models.py -v
python -m pytest tests/test_forward_chaining.py -v
```

### Định Dạng File Đầu Vào

File câu đố phải có định dạng:
```
3
1 < 2 | 3
- - -
2 | 1 > 3
- - -
3 | 2 | 1
```

Trong đó:
- Dòng đầu: Kích thước bảng (N x N)
- Các dòng tiếp theo: Số (giá trị đã biết), khoảng trắng, bất đẳng thức (`<`, `>`, `|` cho không có ràng buộc)
- Dấu gạch ngang `-` chỉ bất đẳng thức dọc

### Các Tính Năng

✅ **Thuật Toán Giải**
- Backtracking với Constraint Satisfaction Problem (CSP)
- Lập trình Logic Tiến (Forward Chaining)
- Lập trình Logic Lùi (Backward Chaining)
- A* Search với hàm Heuristic

✅ **Cơ Sở Kiến Thức & Logic**
- Định nghĩa tiên đề và ràng buộc
- Tạo mệnh đề từ quy tắc
- Các hàm tiện ích logic

✅ **Giao Diện Người Dùng**
- GUI hiện đại với customtkinter
- Chế độ dòng lệnh (CLI)
- Tải và chọn file câu đố
- Hiển thị kết quả thời gian thực
- Lựa chọn thuật toán

✅ **Tiện Ích**
- Phân tích file câu đố tiêu chuẩn
- Hàm heuristic cho tìm kiếm thông minh
- Định dạng và lưu kết quả
- Bộ kiểm thử toàn diện

---

## 🇬🇧 English

### Introduction

**Futoshiki Solver** is a comprehensive tool for solving Futoshiki puzzles using multiple AI algorithms. This is an educational project developed by a team of students to apply knowledge of logic programming, AI search techniques, and user interface design.

Futoshiki (不等式, meaning "inequality") is a logic puzzle similar to Sudoku. The goal is to fill a grid with numbers such that:
- Each row contains unique numbers from 1 to N
- Each column contains unique numbers from 1 to N
- All inequality constraints are satisfied

### System Requirements

- **Python**: >= 3.7 (recommended >= 3.8)
- **Operating System**: Windows, macOS, Linux
- **Memory**: Minimum 512 MB
- **Disk Space**: 500 MB for libraries (with full installation)

### Installation

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd futoshiki-solver
```

#### 2. Create and Activate Virtual Environment

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

To install additional development tools (linting, testing, documentation):
```bash
pip install -r requirements-dev.txt
```

### Project Structure

```
futoshiki-solver/
├── src/                         # Main source code
│   ├── logic/                   # Logic reasoning and constraints
│   │   ├── axioms.py           # Axioms and constraints definition
│   │   ├── grounding.py        # Ground propositions from rules
│   │   └── logic_utils.py      # Utility functions for logic
│   ├── models/                  # Data structures
│   │   ├── board.py            # Puzzle board representation
│   │   ├── kb.py               # Knowledge base
│   │   └── state.py            # Search state
│   ├── solvers/                 # Algorithm implementations
│   │   ├── backtracking.py      # Backtracking solver with CSP
│   │   ├── forward_chaining.py  # Forward chaining logic programming
│   │   ├── backward_chaining.py # Backward chaining logic programming
│   │   └── a_star.py            # A* search with heuristics
│   └── utils/                   # Helper functions
│       ├── heuristic.py         # Heuristic functions
│       └── parser.py            # Puzzle file parser
├── gui/                         # Tkinter GUI components
│   ├── app.py                   # Main GUI application
│   ├── board_frame.py           # Board display
│   ├── sidebar.py               # Control sidebar
│   ├── controller.py            # MVC controller
│   ├── bridge.py                # Data format bridge
│   └── README.md                # GUI documentation
├── tests/                       # Test suite
│   ├── test_models.py
│   ├── test_models_advanced.py
│   ├── test_forward_chaining.py
│   ├── test_heuristic.py
│   └── run_tests.py
├── inputs/                      # Sample puzzle files
│   ├── input-01.txt
│   ├── input-02.txt
│   └── ... (up to 10 files)
├── outputs/                     # Directory for solutions
├── main.py                      # Entry point (GUI & CLI)
├── requirements.txt             # Python dependencies
├── pyproject.toml              # Project configuration
└── README.md                    # This file
```

### Usage Guide

#### Method 1: Run GUI Interface (Recommended)

Launch the graphical interface:
```bash
python main.py
```

The GUI application offers:
- Load puzzle files from the `inputs/` directory
- Select solver algorithm: Backtracking, Forward Chaining, Backward Chaining, A* Search
- View solutions in real-time
- Save results to the `outputs/` directory

#### Method 2: Run from Command Line (CLI)

Solve a specific puzzle using a chosen algorithm:
```bash
python main.py --cli --input inputs/input-01.txt --solver backtracking --output outputs/
```

**Parameters:**
- `--input`: Path to puzzle file (required)
- `--solver`: Algorithm to use: `backtracking`, `forward_chaining`, `backward_chaining`, `a_star` (required)
- `--output`: Output directory or file path (default: `outputs/`)
- `--verbose`: Display detailed logs (optional)

**Examples:**
```bash
# Solve input-01.txt using backtracking
python main.py --cli --input inputs/input-01.txt --solver backtracking

# Solve input-02.txt using A* with verbose output
python main.py --cli --input inputs/input-02.txt --solver a_star --output my_outputs/ --verbose
```

#### Method 3: Run Tests

Run the complete test suite:
```bash
python tests/run_tests.py
```

Or run specific tests:
```bash
python -m pytest tests/test_models.py -v
python -m pytest tests/test_forward_chaining.py -v
```

### Input File Format

Puzzle files must follow this format:
```
3
1 < 2 | 3
- - -
2 | 1 > 3
- - -
3 | 2 | 1
```

Where:
- First line: Board size (N x N)
- Following lines: Numbers (known values), spaces, inequalities (`<`, `>`, `|` for no constraint)
- Dashes `-` indicate vertical inequalities

### Features

✅ **Solving Algorithms**
- Backtracking with Constraint Satisfaction Problem (CSP)
- Forward Chaining Logic Programming
- Backward Chaining Logic Programming
- A* Search with Heuristic Functions

✅ **Knowledge Base & Logic**
- Axiom and constraint definitions
- Proposition grounding from rules
- Logical utility functions

✅ **User Interface**
- Modern GUI with customtkinter
- Command-line interface (CLI)
- Puzzle file loader and selection
- Real-time solution display
- Multiple algorithm selection

✅ **Utilities**
- Standard puzzle file parser
- Heuristic functions for intelligent search
- Solution formatting and saving
- Comprehensive test suite

---

### Notes / Ghi Chú

- **Tiếng Việt**: Đảm bảo rằng file câu đố được lưu với mã hóa UTF-8 nếu có ký tự Việt
- **English**: Ensure puzzle files are saved with UTF-8 encoding for compatibility

For more information, visit the GUI [documentation](gui/README.md).
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python main.py  # GUI mode (default)
# or
python main.py --cli --input inputs/4x4_matrix.txt --solver backtracking  # CLI mode
```

## Usage

### GUI Mode (Interactive)
```bash
python main.py
```
Launches the modern Tkinter GUI where you can:
- Load puzzles from the inputs/ directory
- Select a solver algorithm
- Watch the solution being computed
- View results in the board display

### CLI Mode (Command Line)
```bash
python main.py --cli --input inputs/puzzle.txt --solver backtracking
```

### Available Solvers
- `backtracking` - Standard backtracking with constraint satisfaction
- `forward_chaining` - Logic programming approach
- `backward_chaining` - Logic programming approach
- `a_star` - A* search with heuristics

### CLI Options
- `--input` **(required)**: Path to input puzzle file
- `--solver` **(required)**: Solver algorithm (backtracking, forward_chaining, backward_chaining, a_star)
- `--output` **(optional)**: Path to save solution (default: outputs/)
- `--verbose` **(optional)**: Enable detailed logging

### Input Format
Puzzle files use standard Futoshiki format with numbers and inequality symbols (e.g., `<`, `>`, `^`, `v`).

## Testing

Run the test suite:
```bash
python tests/run_tests.py
# or with pytest
pytest tests/ -v
pytest tests/ --cov  # With coverage report
```

### Test Coverage
- `test_models.py` - Board and state model tests
- `test_models_advanced.py` - Advanced model tests
- `test_forward_chaining.py` - Forward chaining solver tests

## Performance & Benchmarking

Comprehensive benchmarks and performance analysis:
- See `doc/OPTIMIZATION_ANALYSIS.md` for algorithm complexity analysis
- See `benchmark.py` for running performance benchmarks
- See `experiments/` for detailed experiment scripts and results

Key documents:
- [TECHNICAL_ARCHITECTURE.md](doc/TECHNICAL_ARCHITECTURE.md) - System design
- [OPTIMIZATION_IMPLEMENTATION.md](doc/OPTIMIZATION_IMPLEMENTATION.md) - Performance optimizations
- [TEST_RESULTS.md](doc/TEST_RESULTS.md) - Test execution results

## Documentation

Comprehensive documentation available in `doc/`:
- [DOCUMENTATION_INDEX.md](doc/DOCUMENTATION_INDEX.md) - Documentation overview
- [GUI_DEVELOPMENT_GUIDE.md](doc/GUI_DEVELOPMENT_GUIDE.md) - GUI development
- [TESTING_GUIDE.md](doc/TESTING_GUIDE.md) - Testing procedures
- [QUICK_REFERENCE.md](doc/QUICK_REFERENCE.md) - Quick start reference

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`python tests/run_tests.py`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Project Status

✅ **Active Development** - Core features implemented and tested
- All solvers functional and tested
- GUI fully operational
- CLI mode working
- Comprehensive test suite in place
