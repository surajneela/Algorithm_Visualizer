import tkinter as tk
from tkinter import ttk
import math
import queue
import threading
import time

class Node:
    def __init__(self, node_id, x, y):
        self.id = str(node_id)
        self.x = x
        self.y = y
        self.color = "white"
        self.visited = False
        self.radius = 20

class Edge:
    def __init__(self, source, destination):
        self.source = source
        self.destination = destination

class GraphWizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GraphWiz - Algorithm Visualizer (Python)")
        self.root.geometry("800x600")

        self.nodes = []
        self.edges = []
        self.history = [] # Stack for undo (stores objects created)
        self.selected_node = None
        self.running_algorithm = False

        # --- UI Layout ---
        self.main_container = tk.Frame(root)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Graph Canvas
        self.canvas = tk.Canvas(self.main_container, bg="#f0f0f0", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, side=tk.TOP)
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<Button-3>", self.on_right_click) # Right click (Windows/Linux)
        self.canvas.bind("<Button-2>", self.on_right_click) # MacOS often uses Button-2 for right click context

        # Bottom Panel
        self.bottom_panel = tk.Frame(root, pady=10)
        self.bottom_panel.pack(fill=tk.X, side=tk.BOTTOM)

        # Status Label
        self.status_var = tk.StringVar()
        self.status_var.set("Traversal Path: ")
        self.status_label = tk.Label(self.bottom_panel, textvariable=self.status_var, font=("Arial", 12, "bold"))
        self.status_label.pack(side=tk.TOP, pady=(0, 10))

        # Controls
        self.controls_frame = tk.Frame(self.bottom_panel)
        self.controls_frame.pack(side=tk.TOP)

        ttk.Button(self.controls_frame, text="Run BFS", command=self.run_bfs).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.controls_frame, text="Run DFS", command=self.run_dfs).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.controls_frame, text="Undo", command=self.undo).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.controls_frame, text="Reset", command=self.reset_graph).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.controls_frame, text="Clear", command=self.clear_graph).pack(side=tk.LEFT, padx=5)

    def draw(self):
        self.canvas.delete("all")

        # Draw Edges
        for edge in self.edges:
            self.canvas.create_line(edge.source.x, edge.source.y, 
                                    edge.destination.x, edge.destination.y, 
                                    width=2, fill="black")

        # Draw Nodes
        for node in self.nodes:
            # Highlight border if selected
            outline_color = "black"
            width = 1
            if node == self.selected_node:
                self.canvas.create_oval(node.x - node.radius - 3, node.y - node.radius - 3,
                                        node.x + node.radius + 3, node.y + node.radius + 3,
                                        fill="", outline="yellow", width=3)
            
            # Fill color based on state
            fill_color = node.color
            
            self.canvas.create_oval(node.x - node.radius, node.y - node.radius,
                                    node.x + node.radius, node.y + node.radius,
                                    fill=fill_color, outline=outline_color, width=width)
            
            self.canvas.create_text(node.x, node.y, text=node.id, font=("Arial", 10, "bold"))

    def get_node_at(self, x, y):
        for node in self.nodes:
            dist = math.sqrt((x - node.x)**2 + (y - node.y)**2)
            if dist <= node.radius:
                return node
        return None

    def on_left_click(self, event):
        if self.running_algorithm: return

        x, y = event.x, event.y
        clicked_node = self.get_node_at(x, y)

        if clicked_node:
            if self.selected_node is None:
                self.selected_node = clicked_node
            else:
                if self.selected_node != clicked_node:
                    # Create Edge
                    self.add_edge(self.selected_node, clicked_node)
                self.selected_node = None # Deselect after action
        else:
            # Create Node
            self.add_node(x, y)
        
        self.draw()

    def on_right_click(self, event):
        if self.running_algorithm: return
        if self.selected_node:
            self.selected_node = None
            self.draw()

    def add_node(self, x, y):
        node = Node(len(self.nodes), x, y)
        self.nodes.append(node)
        self.history.append(node)

    def add_edge(self, u, v):
        # Prevent duplicates
        for edge in self.edges:
            if (edge.source == u and edge.destination == v) or \
               (edge.source == v and edge.destination == u):
                return
        
        edge = Edge(u, v)
        self.edges.append(edge)
        self.history.append(edge)

    def undo(self):
        if self.running_algorithm: return
        if not self.history: return

        item = self.history.pop()
        if isinstance(item, Node):
            if item in self.nodes:
                self.nodes.remove(item)
                # Remove connected edges
                self.edges = [e for e in self.edges if e.source != item and e.destination != item]
                if self.selected_node == item:
                    self.selected_node = None
        elif isinstance(item, Edge):
            if item in self.edges:
                self.edges.remove(item)
        
        self.draw()

    def reset_graph(self):
        if self.running_algorithm: return
        for node in self.nodes:
            node.color = "white"
            node.visited = False
        self.status_var.set("Traversal Path: ")
        self.draw()

    def clear_graph(self):
        if self.running_algorithm: return
        self.nodes = []
        self.edges = []
        self.history = []
        self.selected_node = None
        self.status_var.set("Traversal Path: ")
        self.draw()

    # --- ALGORITHMS ---

    def run_bfs(self):
        if self.running_algorithm or not self.nodes: return
        
        self.reset_graph()
        self.running_algorithm = True
        start_node = self.nodes[0]
        
        threading.Thread(target=self._bfs_logic, args=(start_node,), daemon=True).start()

    def _bfs_logic(self, start_node):
        path = []
        q = queue.Queue()
        q.put(start_node)
        start_node.visited = True
        start_node.color = "#90EE90" # Light Green
        
        self.update_ui_deferred(path, start_node.id)

        while not q.empty():
            current = q.get()
            
            if current != start_node:
                current.color = "orange"
                self.refresh_ui()
            
            time.sleep(0.5)

            # Get neighbors
            neighbors = []
            for edge in self.edges:
                if edge.source == current: neighbors.append(edge.destination)
                elif edge.destination == current: neighbors.append(edge.source)
            
            # Sort by ID for consistent traversal if needed, though Set behavior implies defined graph order
            neighbors.sort(key=lambda n: int(n.id))

            for neighbor in neighbors:
                if not neighbor.visited:
                    neighbor.visited = True
                    neighbor.color = "cyan"
                    q.put(neighbor)
                    self.update_ui_deferred(path, neighbor.id)
                    time.sleep(0.3)
            
            current.color = "#6495ED" # Cornflower Blue (Processed)
            self.refresh_ui()

        self.running_algorithm = False

    def run_dfs(self):
        if self.running_algorithm or not self.nodes: return
        
        self.reset_graph()
        self.running_algorithm = True
        start_node = self.nodes[0]

        threading.Thread(target=self._dfs_logic, args=(start_node,), daemon=True).start()

    def _dfs_logic(self, start_node):
        path = []
        self._dfs_recursive(start_node, path)
        self.running_algorithm = False

    def _dfs_recursive(self, current, path):
        current.visited = True
        current.color = "orange"
        self.update_ui_deferred(path, current.id)
        
        time.sleep(0.5)

        neighbors = []
        for edge in self.edges:
            if edge.source == current: neighbors.append(edge.destination)
            elif edge.destination == current: neighbors.append(edge.source)
        
        neighbors.sort(key=lambda n: int(n.id))

        for neighbor in neighbors:
            if not neighbor.visited:
                self._dfs_recursive(neighbor, path)
        
        current.color = "#6495ED"
        self.refresh_ui()

    def update_ui_deferred(self, path_list, new_id):
        path_list.append(new_id)
        path_str = "-".join(path_list)
        self.root.after(0, lambda: self.status_var.set(f"Traversal Path: {path_str}"))
        self.root.after(0, self.draw)

    def refresh_ui(self):
        self.root.after(0, self.draw)


if __name__ == "__main__":
    root = tk.Tk()
    app = GraphWizApp(root)
    root.mainloop()
