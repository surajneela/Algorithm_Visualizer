import tkinter as tk
from tkinter import ttk
import math
import queue
import threading
import time

# --- Configuration & Aesthetics ---
THEME = {
    "bg_color": "#ffffff",           # White background
    "canvas_bg": "#fafafa",          # Very light grey for canvas
    "node_fill": "#ffffff",          # Node fill
    "node_outline": "#000000",       # Solid black outline
    "edge_color": "#333333",         # Dark grey/black edges
    "text_color": "#000000",         # Black text
    "accent_color": "#007acc",       # VS Code blue for highlights
    "visited_color": "#98fb98",      # Pale Green
    "processing_color": "#ffd700",   # Gold/Yellow
    "finished_color": "#87cefa",     # Light Sky Blue
    "shadow_color": "#dddddd",       # Light shadow
    "font_main": ("Segoe UI", 12, "bold"),
    "font_node": ("Segoe UI", 10, "bold")
}

class Node:
    def __init__(self, node_id, x, y):
        self.id = str(node_id)
        self.x = x
        self.y = y
        self.color = THEME["node_fill"]
        self.target_color = THEME["node_fill"] # For animation (future use)
        self.visited = False
        self.radius = 24  # Slightly larger for better touch targets

class Edge:
    def __init__(self, source, destination):
        self.source = source
        self.destination = destination

class GraphWizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GraphWiz - Modern Visualizer")
        self.root.geometry("1000x700")
        self.root.configure(bg=THEME["bg_color"])

        self.nodes = []
        self.edges = []
        self.history = []
        self.selected_node = None
        self.running_algorithm = False

        self._setup_ui()

    def _setup_ui(self):
        # Configure Styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background=THEME["bg_color"])
        style.configure("TButton", 
                        padding=10, 
                        relief="flat", 
                        background=THEME["accent_color"], 
                        foreground="white",
                        font=("Segoe UI", 10, "bold"))
        style.map("TButton", background=[("active", "#005f9e")])

        # Main Layout
        self.header_label = tk.Label(self.root, text="GraphWiz Visualizer", 
                                     bg=THEME["bg_color"], fg="white", 
                                     font=("Segoe UI", 18, "bold"), pady=15)
        self.header_label.pack(side=tk.TOP, fill=tk.X)

        self.canvas_frame = tk.Frame(self.root, bg=THEME["bg_color"], padx=20, pady=10)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, bg=THEME["canvas_bg"], 
                                highlightthickness=0, relief="flat")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Rounded corners effect (simulated via bordering frame if needed, but canvas is rect)
        
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<Button-2>", self.on_right_click)

        # Bottom Controls
        self.controls_panel = tk.Frame(self.root, bg=THEME["bg_color"], pady=20)
        self.controls_panel.pack(side=tk.BOTTOM, fill=tk.X)

        # Status
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to Build... Drag nodes to move!")
        self.status_label = tk.Label(self.controls_panel, textvariable=self.status_var, 
                                     bg=THEME["bg_color"], fg="#d4d4d4",
                                     font=("Consolas", 12))
        self.status_label.pack(side=tk.TOP, pady=(0, 15))

        # Button Bar
        self.btn_frame = tk.Frame(self.controls_panel, bg=THEME["bg_color"])
        self.btn_frame.pack(side=tk.TOP)

        self.create_button("Run BFS", self.run_bfs)
        self.create_button("Run DFS", self.run_dfs)
        self.create_spacer()
        self.create_button("Undo", self.undo, bg="#dda448")
        self.create_button("Reset", self.reset_graph, bg="#6e7681")
        self.create_button("Clear", self.clear_graph, bg="#d9534f")

    def create_button(self, text, command, bg=None):
        btn = tk.Button(self.btn_frame, text=text, command=command,
                        bg=bg if bg else THEME["accent_color"],
                        fg="white", activebackground=THEME["node_fill"],
                        activeforeground="black", relief="flat",
                        padx=20, pady=8, font=("Segoe UI", 10, "bold"),
                        cursor="hand2", borderwidth=0)
        btn.pack(side=tk.LEFT, padx=8)

    def create_spacer(self):
        tk.Label(self.btn_frame, text="|", bg=THEME["bg_color"], fg="#444", font=("Arial", 14)).pack(side=tk.LEFT, padx=10)

    # --- Drawing Logic (Smooth Aesthetics) ---
    def draw(self):
        self.canvas.delete("all")

        # Draw Edges (Anti-aliasing simulated by thickness)
        for edge in self.edges:
            self.canvas.create_line(edge.source.x, edge.source.y, 
                                    edge.destination.x, edge.destination.y, 
                                    width=3, fill=THEME["edge_color"], capstyle=tk.ROUND, smooth=True)

        # Draw Nodes with simple shadow
        for node in self.nodes:
            # Shadow
            self.canvas.create_oval(node.x - node.radius + 3, node.y - node.radius + 3,
                                    node.x + node.radius + 3, node.y + node.radius + 3,
                                    fill="#111111", outline="", tags="shadow")
            
            # Glow / Selection ring
            if node == self.selected_node:
                self.canvas.create_oval(node.x - node.radius - 4, node.y - node.radius - 4,
                                        node.x + node.radius + 4, node.y + node.radius + 4,
                                        outline=THEME["accent_color"], width=3)

            # Main Node Body
            self.canvas.create_oval(node.x - node.radius, node.y - node.radius,
                                    node.x + node.radius, node.y + node.radius,
                                    fill=node.color, outline=THEME["node_outline"], width=0)
            
            # Text ID
            self.canvas.create_text(node.x, node.y, text=node.id, 
                                    fill=THEME["text_color"], font=THEME["font_node"])

    # --- Interaction Logic ---
    def get_node_at(self, x, y):
        for node in self.nodes:
            dist = math.sqrt((x - node.x)**2 + (y - node.y)**2)
            if dist <= node.radius + 5: # Bit of tolerance
                return node
        return None

    # Drag and Drop Logic
    def on_mouse_down(self, event):
        if self.running_algorithm: return
        self.drag_node = self.get_node_at(event.x, event.y)
        self.is_dragging = False

    def on_mouse_drag(self, event):
        if self.running_algorithm: return
        if self.drag_node:
            self.is_dragging = True
            self.drag_node.x = event.x
            self.drag_node.y = event.y
            self.draw() # Live update

    def on_mouse_up(self, event):
        if self.running_algorithm: return
        
        # If we were dragging, just stop dragging and return
        if self.is_dragging:
            self.drag_node = None
            self.is_dragging = False
            self.status_var.set("Moved Node")
            return

        # Explicit click logic (Was not dragging)
        x, y = event.x, event.y
        clicked_node = self.get_node_at(x, y)

        if clicked_node:
            if self.selected_node is None:
                self.selected_node = clicked_node
                self.status_var.set(f"Selected Node {clicked_node.id}")
            else:
                if self.selected_node != clicked_node:
                    self.add_edge(self.selected_node, clicked_node)
                    self.status_var.set(f"Connected {self.selected_node.id} -> {clicked_node.id}")
                else:
                    self.status_var.set("Deselected")
                self.selected_node = None
        else:
            self.add_node(x, y)
            self.status_var.set("Added Node")
        
        self.drag_node = None
        self.draw()

    def on_right_click(self, event):
        if self.running_algorithm: return
        if self.selected_node:
            self.selected_node = None
            self.status_var.set("Deselected")
            self.draw()

    def add_node(self, x, y):
        node = Node(len(self.nodes), x, y)
        self.nodes.append(node)
        self.history.append(node)

    def add_edge(self, u, v):
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
                self.edges = [e for e in self.edges if e.source != item and e.destination != item]
                if self.selected_node == item: self.selected_node = None
        elif isinstance(item, Edge):
            if item in self.edges:
                self.edges.remove(item)
        self.draw()
        self.status_var.set("Undo Action")

    def reset_graph(self):
        if self.running_algorithm: return
        for node in self.nodes:
            node.color = THEME["node_fill"]
            node.visited = False
        self.status_var.set("Graph Reset")
        self.draw()

    def clear_graph(self):
        if self.running_algorithm: return
        self.nodes = []
        self.edges = []
        self.history = []
        self.selected_node = None
        self.status_var.set("Graph Cleared")
        self.draw()

    # --- ALGORITHMS ---
    def run_bfs(self):
        if self.running_algorithm or not self.nodes: return
        self.reset_graph()
        self.running_algorithm = True
        self.status_var.set("Running BFS...")
        threading.Thread(target=self._bfs_logic, args=(self.nodes[0],), daemon=True).start()

    def _bfs_logic(self, start_node):
        path = []
        q = queue.Queue()
        q.put(start_node)
        start_node.visited = True
        start_node.color = THEME["visited_color"]
        
        self.update_ui_deferred(path, start_node.id)

        while not q.empty():
            current = q.get()
            
            if current != start_node:
                current.color = THEME["processing_color"]
                self.refresh_ui()
            
            time.sleep(0.6)

            neighbors = self._get_neighbors(current)
            for neighbor in neighbors:
                if not neighbor.visited:
                    neighbor.visited = True
                    neighbor.color = THEME["visited_color"]
                    q.put(neighbor)
                    self.update_ui_deferred(path, neighbor.id)
                    time.sleep(0.4)
            
            current.color = THEME["finished_color"]
            self.refresh_ui()

        self.running_algorithm = False
        self.root.after(0, lambda: self.status_var.set(f"BFS Complete! Path: {'-'.join(path)}"))

    def run_dfs(self):
        if self.running_algorithm or not self.nodes: return
        self.reset_graph()
        self.running_algorithm = True
        self.status_var.set("Running DFS...")
        threading.Thread(target=self._dfs_logic, args=(self.nodes[0],), daemon=True).start()

    def _dfs_logic(self, start_node):
        path = []
        self._dfs_recursive(start_node, path)
        self.running_algorithm = False
        self.root.after(0, lambda: self.status_var.set(f"DFS Complete! Path: {'-'.join(path)}"))

    def _dfs_recursive(self, current, path):
        current.visited = True
        current.color = THEME["processing_color"]
        self.update_ui_deferred(path, current.id)
        
        time.sleep(0.6)

        neighbors = self._get_neighbors(current)
        for neighbor in neighbors:
            if not neighbor.visited:
                self._dfs_recursive(neighbor, path)
        
        current.color = THEME["finished_color"]
        self.refresh_ui()

    def _get_neighbors(self, node):
        neighbors = []
        for edge in self.edges:
            if edge.source == node: neighbors.append(edge.destination)
            elif edge.destination == node: neighbors.append(edge.source)
        neighbors.sort(key=lambda n: int(n.id))
        return neighbors

    def update_ui_deferred(self, path_list, new_id):
        path_list.append(new_id)
        path_str = " -> ".join(path_list)
        # Use simple blinking effect or just update
        self.root.after(0, lambda: self.status_var.set(f"Path: {path_str}"))
        self.root.after(0, self.draw)

    def refresh_ui(self):
        self.root.after(0, self.draw)


if __name__ == "__main__":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1) # Enable high-DPI scaling on Windows
    except:
        pass
        
    root = tk.Tk()
    app = GraphWizApp(root)
    root.mainloop()
