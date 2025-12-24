# GraphWiz

**GraphWiz** is a simple and catchy Graph Algorithm Visualizer built with Java Swing. It allows you to draw graphs interactively and watch how BFS (Breadth-First Search) and DFS (Depth-First Search) algorithms traverse them.

## Features
- **Design Your Graph**:
  - **Click** to create nodes.
  - **Click two nodes** to connect them with an edge.
  - **Undo** button to fix mistakes easily.
- **Visualize Algorithms**: Watch BFS and DFS in action with color-coded steps.
- **Live Path Logging**: See the traversal path (e.g., `0-1-4-3`) generated in real-time.
- **Interactive Control**: Reset or Clear the board to start fresh.

## How to Run

### Prerequisites
- Java JDK installed (Java 8 or higher).

### Compile and Run
1. Open your terminal in the project folder.
2. Compile the code:
   ```bash
   javac -d bin src/main/java/com/graphwiz/*.java
   ```
3. Run the application:
   ```bash
   java -cp bin com.graphwiz.GraphWiz
   ```

## Controls
- **Left Click**: Add Node / Select Node
- **Right Click**: Deselect Node
- **Undo**: Remove the last added node or edge.
- **Run BFS / DFS**: Start the visualization.
- **Reset**: clear colors.
- **Clear**: Delete the entire graph.

## Project Structure

```text
Algorithm_Visualizer/
├── src/
│   └── main/
│       └── java/
│           └── com/
│               └── graphwiz/
│                   ├── GraphWiz.java       # Main entry point and UI frame
│                   ├── GraphPanel.java     # Drawing canvas and mouse interaction logic
│                   ├── Node.java           # Data model for Graph Nodes
│                   └── Edge.java           # Data model for Graph Edges
├── bin/                                    # Compiled Java bytecode (.class files)
├── README.md                               # Project documentation
└── .gitignore                              # Git configuration
```