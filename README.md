# Algorithm Visualizer

**Algorithm Visualizer** is a collection of Python-based GUI applications designed to demonstrate various computer science algorithms. From searching and sorting to pathfinding, this repository offers interactive visualizations to help you understand how these algorithms work.

## 🚀 Available Algorithms

The following algorithms are available to explore:

### Searching

- **Linear Search**: Visualizes checking each element in a list sequentially until the target is found.
- **Binary Search**: Demonstrates the efficient divide-and-conquer approach on a sorted list.

### Sorting

- **Bubble Sort**: Shows the step-by-step process of bubbling the largest elements to the top.

### Pathfinding & Graph Traversal

- **BFS & DFS (GraphWiz)**: Interactive graph builder to visualize Breadth-First Search and Depth-First Search.
- **Dijkstra's Algorithm**:
  - `dijkstra.py`: Standard graph visualization finding the shortest path.
  - `dijkstra_maze_solver.py`: A grid-based maze solver using Dijkstra's algorithm.
- **A\* Search**:
  - `a_star.py`: Pathfinding on a graph.
  - `a_star_maze_solver.py`: Optimized maze solving using heuristics.

### Comparisons

- **Maze Comparison**: `compare_maze.py` allows you to visually compare the performance of different pathfinding algorithms (e.g., Dijkstra vs. A\*) side-by-side.

---

## 🛠️ How to Run

### Prerequisites

- Python 3.x installed on your system.
- `tkinter` (usually comes pre-installed with Python).

### Instructions

1.  **Clone the Repository** (if you haven't already):

    ```bash
    git clone https://github.com/surajneela/Algorithm_Visualizer.git
    cd Algorithm_Visualizer
    ```

2.  **Navigate and Run**:
    Open your terminal or command prompt and run the specific file for the algorithm you want to see.

    **Linear Search**

    ```bash
    python Linear_Search/linear_search.py
    ```

    **Binary Search**

    ```bash
    python Binary_Search/binary_search.py
    ```

    **Bubble Sort**

    ```bash
    python Bubble_Sort/bubble_sort.py
    ```

    **BFS & DFS (GraphWiz)**

    ```bash
    python BFS_DFS/main.py
    ```

    **Dijkstra's Algorithm**

    ```bash
    python Dijkstra/dijkstra.py
    # OR for the maze solver
    python Dijkstra/dijkstra_maze_solver.py
    ```

    **A\* Search**

    ```bash
    python A_Star/a_star.py
    # OR for the maze solver
    python A_Star/a_star_maze_solver.py
    ```

    **Algorithm Comparison**

    ```bash
    python Comparison/compare_maze.py
    ```

---

## 🎮 Features

- **Interactive Input**: Most visualizers allow you to input custom data or generate random datasets.
- **Step-by-Step Animation**: Watch the algorithms execute in real-time with adjustable speeds (in some apps).
- **Visual Feedback**: Color-coded elements show current state (e.g., checking, found, visited, path).

Enjoy exploring the algorithms!
