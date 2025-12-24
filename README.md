# Algorithm Visualizer

A Java Swing application to visualize BFS and DFS algorithms on a graph.

## Features
- Interactive Graph Creation:
  - **Left Click**: Add a node.
  - **Left Click two nodes**: Add an edge between them. (Click one to select, then click another to connect).
  - **Right Click**: Deselect current node.
- **BFS Visualization**: Breadth-First Search animation.
- **DFS Visualization**: Depth-First Search animation.
- **Reset**: Resets colors and visited status.
- **Clear**: Clears the entire graph.

## How to Run

### Prerequisites
- Java JDK installed (Java 8+ recommended).

### Compile
Run the following command from the project root:
```bash
mkdir bin
javac -d bin src/main/java/com/visualizer/*.java
```

### Run
```bash
java -cp bin com.visualizer.AlgorithmVisualizer
```