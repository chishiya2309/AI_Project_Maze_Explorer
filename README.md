# 🧩 Maze Explorer

[🇻🇳 Tiếng Việt](#-tiếng-việt) | [🇬🇧 English](#-english)

---

## 🎥 Demo Video

https://github.com/user-attachments/assets/b35afd27-ba63-4c33-9da1-94408e466de0

https://github.com/user-attachments/assets/e9cebc3f-66f8-4f30-ae47-e7574eff682c

---

## 🇻🇳 Tiếng Việt

**Maze Explorer** là một dự án trực quan hóa các thuật toán tìm kiếm trí tuệ nhân tạo (AI Search Algorithms) cổ điển trong không gian 2D, được xây dựng bằng Python và Pygame. 
Điểm đặc biệt của project là bài toán tìm đường đi không chỉ đơn thuần là tìm đường từ điểm Bắt đầu (S) đến điểm Kết thúc (G), mà agent còn bắt buộc phải **thu thập toàn bộ các ngôi sao (Stars)** xuất hiện trên bản đồ trước khi thoát khỏi mê cung.

### 🌟 Tính năng nổi bật (Features)
- **Hỗ trợ 5 thuật toán tìm kiếm AI**: Breadth-First Search (BFS), Depth-First Search (DFS), Uniform Cost Search (UCS), Greedy Best-First Search, và A* Search.
- **Tối ưu hóa A***: Sử dụng hàm Heuristic kết hợp với thuật toán Minimum Spanning Tree (MST) để đánh giá đường đi qua nhiều điểm (thu thập nhiều sao) mang lại kết quả đường đi ngắn nhất với số nút mở rộng tối thiểu.
- **Trực quan hóa sinh động**: Quá trình duyệt nút (nodes expansion) và đường đi tìm được (reconstructed path) được hiển thị trực tiếp với màu sắc rõ ràng (Màu xanh ngọc cho nút đang mở rộng, Xanh lá cho đường đi hoàn chỉnh).
- **Trình chỉnh sửa bản đồ (Map Editor)**: Cho phép tự thiết kế mê cung, đặt vị trí Bắt đầu, Kết thúc và các Ngôi sao.
- **Lưu lịch sử (Stats)**: Lưu trữ điểm số, thời gian, số bước đi, số nút mở rộng của các lượt chơi vào `stats.json`.

### 🧠 Khía cạnh Thuật toán (Algorithm Focus)
Project tập trung sâu vào việc phân tích và đánh giá hiệu suất của các thuật toán:
1. **Tìm kiếm mù (Uninformed Search)**:
   - **BFS**: Tìm được đường đi tối ưu nhưng tốn rất nhiều bộ nhớ và thời gian để mở rộng nút (duyệt diện rộng).
   - **DFS**: Tiết kiệm bộ nhớ hơn nhưng đường đi tìm được thường rất tệ và không tối ưu (do đi sâu vào nhánh sai và mất thời gian backtrack).
   - **UCS**: Tương tự BFS trong đồ thị có trọng số cạnh bằng nhau, luôn đảm bảo kết quả đường đi ngắn nhất.
2. **Tìm kiếm có thông tin (Informed / Heuristic Search)**:
   - **Greedy Best-First Search**: Dùng Heuristic khoảng cách Manhattan, tìm lời giải rất nhanh do luôn hướng về đích nhưng kết quả không phải lúc nào cũng là tối ưu.
   - **A* Search**: Là thuật toán toàn diện nhất. Bằng cách kết hợp chi phí thực tế $g(n)$ và hàm Heuristic chấp nhận được $h(n)$ (sử dụng tính toán Minimum Spanning Tree cho các điểm sao chưa ăn), A* luôn đảm bảo tìm ra con đường tối ưu nhất với số lượng nút phải duyệt ít hơn rất nhiều so với BFS/UCS.

### 🚀 Cài đặt nhanh (Quick Start)

**Yêu cầu hệ thống:** Python 3.7+ (Khuyến nghị sử dụng Python 3.12 trở xuống do `pygame` không hỗ trợ `distutils` trên Python 3.14, hoặc sử dụng `pygame-ce` như cấu hình hiện tại).

```bash
# Clone repository
git clone https://github.com/chishiya2309/AI_Project_Maze_Explorer.git
cd AI_Project_Maze_Explorer

# (Khuyến khích) Tạo môi trường ảo
python -m venv venv
venv\Scripts\activate # Trên Windows
# source venv/bin/activate # Trên macOS/Linux

# Cài đặt thư viện
pip install -r requirements.txt

# Khởi chạy game
python main.py
```

---

## 🇬🇧 English

**Maze Explorer** is an AI Search Algorithms visualization project built with Python and Pygame in a 2D grid environment. 
The unique challenge in this project is that the agent cannot just go directly from the Start (S) to the Goal (G); it must **collect all the stars** scattered across the map before the exit unlocks.

### 🌟 Key Features
- **5 AI Search Algorithms Supported**: Breadth-First Search (BFS), Depth-First Search (DFS), Uniform Cost Search (UCS), Greedy Best-First Search, and A* Search.
- **A* Optimization**: Implements an advanced Heuristic function utilizing the Minimum Spanning Tree (MST) approach to evaluate multi-target paths (collecting multiple stars), guaranteeing the optimal path with minimal node expansion.
- **Live Visualization**: Step-by-step visualization of node expansion (exploration) and the reconstructed path using distinct colors.
- **Map Editor**: Built-in level editor to create your own mazes, place Start/Goal states, and scatter stars.
- **History & Stats**: Records results, time taken, steps, and expanded nodes into `stats.json`.

### 🧠 Algorithm Focus
This project heavily emphasizes comparing the performance and nature of different search algorithms:
1. **Uninformed Search**:
   - **BFS**: Guarantees the optimal path but consumes massive memory and time expanding nodes across the board.
   - **DFS**: Memory efficient but rarely finds the optimal path (often gets lost in deep sub-optimal branches).
   - **UCS**: Behaves like BFS in unweighted grids, always guarantees the optimal path.
2. **Informed (Heuristic) Search**:
   - **Greedy Best-First Search**: Uses Manhattan distance heuristic, finds a solution extremely quickly but the path is often sub-optimal.
   - **A* Search**: The most balanced algorithm. By combining the actual cost $g(n)$ and an admissible heuristic $h(n)$ (MST computation for remaining stars), A* perfectly guarantees the most optimal path while expanding significantly fewer nodes compared to BFS or UCS.

### 🚀 Quick Start

**Prerequisites:** Python 3.7+

```bash
# Clone repository
git clone https://github.com/chishiya2309/AI_Project_Maze_Explorer.git
cd AI_Project_Maze_Explorer

# (Recommended) Create virtual environment
python -m venv venv
venv\Scripts\activate # On Windows
# source venv/bin/activate # On macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py
```
