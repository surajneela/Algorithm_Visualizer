import tkinter as tk
from tkinter import simpledialog, messagebox
import math
import heapq
import threading
import time

# --- Configuration & Aesthetics ---
THEME = {
    "bg_color": "#ffffff",
    "canvas_bg": "#fafafa",
    "node_fill": "#ffffff",
    "node_outline": "#000000",
    "edge_color": "#333333",
    "text_color": "#000000",
    "accent_color": "#007acc",
    "start_node": "#00ff00",
    "target_node": "#ff0000",
    "processing_color": "#ffd700",   # Gold
    "finished_color": "#98fb98",     # Pale Green
    "path_color": "#ff4500",         # Orange Red
    "font_main": ("Segoe UI", 12, "bold"),
    "font_node": ("Segoe UI", 10, "bold"),
    "font_edge": ("Segoe UI", 9, "bold")
}

class Node:
    def __init__(self, node_id, x, y):
        self.id = str(node_id)
        self.x = x
        self.y = y
        self.color = THEME["node_fill"]
        self.g_score = float('inf') 
        self.f_score = float('inf')
        self.parent = None
        self.radius = 24

class Edge:
    def __init__(self, source, destination, weight=1):
        self.source = source
        self.destination = destination
        self.weight = weight

class AStarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("A* Algorithm Visualizer (Graph)")
        self.root.geometry("1000x750")
        self.root.configure(bg=THEME["bg_color"])

        self.nodes = []
        self.edges = []
        self.selected_node = None
        
        self.start_node = None
        self.target_node = None
        
        self.running_algorithm = False

        self._setup_ui()

    def _setup_ui(self):
        # Header
        self.header_label = tk.Label(self.root, text="A* Graph Visualizer (Set Start & Target)", 
                                     bg=THEME["bg_color"], fg="black", 
                                     font=("Segoe UI", 16, "bold"), pady=10)
        self.header_label.pack(side=tk.TOP, fill=tk.X)

        # Canvas
        self.canvas_frame = tk.Frame(self.root, bg=THEME["bg_color"], padx=20, pady=10)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, bg=THEME["canvas_bg"], highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        # Right click to set Start/Target contextually? Or just buttons.
        # Let's use Buttons for explicit "Set Start" / "Set Target"

        # Controls
        self.controls_panel = tk.Frame(self.root, bg=THEME["bg_color"], pady=20)
        self.controls_panel.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_var = tk.StringVar()
        self.status_var.set("Click to add nodes. Drag to connect. Select node & click 'Set Start'/'Set Target'.")
        tk.Label(self.controls_panel, textvariable=self.status_var, bg=THEME["bg_color"], font=("Consolas", 11)).pack(pady=(0, 10))

        btn_frame = tk.Frame(self.controls_panel, bg=THEME["bg_color"])
        btn_frame.pack()

        self.create_button(btn_frame, "Set Start", self.set_start, bg="#28a745")
        self.create_button(btn_frame, "Set Target", self.set_target, bg="#dc3545")
        self.create_button(btn_frame, "Run A*", self.run_a_star, bg=THEME["accent_color"])
        self.create_button(btn_frame, "Clear Graph", self.clear_graph, bg="#333")

    def create_button(self, parent, text, command, bg):
        tk.Button(parent, text=text, command=command, bg=bg, fg="white", 
                  relief="flat", padx=15, pady=8, font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=10)

    # --- Interaction ---
    def get_node_at(self, x, y):
        for node in self.nodes:
            if math.sqrt((x - node.x)**2 + (y - node.y)**2) <= node.radius + 5:
                return node
        return None

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
            self.draw()

    def on_mouse_up(self, event):
        if self.running_algorithm: return
        
        if self.is_dragging:
            self.drag_node = None
            self.is_dragging = False
            return

        clicked_node = self.get_node_at(event.x, event.y)

        if clicked_node:
            if self.selected_node is None:
                self.selected_node = clicked_node
                self.status_var.set(f"Selected Node {clicked_node.id}. Connect? Set Start/Target?")
            else:
                if self.selected_node != clicked_node:
                    self.prompt_edge_weight(self.selected_node, clicked_node)
                self.selected_node = None
        else:
            self.add_node(event.x, event.y)
        
        self.drag_node = None
        self.draw()

    def set_start(self):
        if self.selected_node:
            self.start_node = self.selected_node
            self.selected_node = None
            self.status_var.set(f"Start Node set to {self.start_node.id}")
            self.draw()

    def set_target(self):
        if self.selected_node:
            self.target_node = self.selected_node
            self.selected_node = None
            self.status_var.set(f"Target Node set to {self.target_node.id}")
            self.draw()

    def prompt_edge_weight(self, u, v):
        weight = simpledialog.askinteger("Edge Weight", f"Enter weight for {u.id}-{v.id}:", 
                                       parent=self.root, minvalue=1, initialvalue=1)
        if weight is None: weight = 1 
        self.add_edge(u, v, weight)
        self.status_var.set(f"Added Edge {u.id}-{v.id} (Weight: {weight})")

    def add_node(self, x, y):
        node = Node(len(self.nodes), x, y)
        self.nodes.append(node)

    def add_edge(self, u, v, weight):
        self.edges = [e for e in self.edges if not ((e.source==u and e.destination==v) or (e.source==v and e.destination==u))]
        self.edges.append(Edge(u, v, weight))

    def clear_graph(self):
        if self.running_algorithm: return
        self.nodes = []
        self.edges = []
        self.selected_node = None
        self.start_node = None
        self.target_node = None
        self.status_var.set("Graph Cleared")
        self.header_label.config(text="A* Graph Visualizer (Set Start & Target)")
        self.draw()

    def draw(self):
        self.canvas.delete("all")

        # Edges
        for edge in self.edges:
            self.canvas.create_line(edge.source.x, edge.source.y, edge.destination.x, edge.destination.y, 
                                    width=2, fill=THEME["edge_color"])
            mx, my = (edge.source.x + edge.destination.x)/2, (edge.source.y + edge.destination.y)/2
            self.canvas.create_oval(mx-10, my-10, mx+10, my+10, fill="white", outline=THEME["edge_color"])
            self.canvas.create_text(mx, my, text=str(edge.weight), font=THEME["font_edge"])

        # Nodes
        for node in self.nodes:
            fill_color = node.color
            if node == self.start_node: fill_color = THEME["start_node"]
            elif node == self.target_node: fill_color = THEME["target_node"]
            
            outline_width = 1
            outline_col = THEME["node_outline"]
            if node == self.selected_node:
                outline_width = 3
                outline_col = THEME["accent_color"]
            
            self.canvas.create_oval(node.x - node.radius, node.y - node.radius,
                                    node.x + node.radius, node.y + node.radius,
                                    fill=fill_color, outline=outline_col, width=outline_width)
            
            label = node.id
            # Show f, g, h if calculated
            if node.f_score != float('inf'):
                # Short label: f=..
                label += f"\nF:{int(node.f_score)}"
            
            self.canvas.create_text(node.x, node.y, text=label, fill=THEME["text_color"], font=THEME["font_node"])

    # --- A* Algorithm ---
    def heuristic(self, a, b):
        # Euclidean distance
        return math.sqrt((a.x - b.x)**2 + (a.y - b.y)**2)

    def run_a_star(self):
        if self.running_algorithm or not self.start_node or not self.target_node:
            if not self.start_node or not self.target_node:
                messagebox.showwarning("Missing Info", "Please set both Start and Target nodes.")
            return
        
        self.running_algorithm = True
        self.status_var.set(f"Running A* from {self.start_node.id} to {self.target_node.id}...")
        threading.Thread(target=self._a_star_logic, daemon=True).start()

    def _a_star_logic(self):
        # Reset
        for n in self.nodes:
            n.g_score = float('inf')
            n.f_score = float('inf')
            n.parent = None
            n.color = THEME["node_fill"]

        self.start_node.g_score = 0
        self.start_node.f_score = self.heuristic(self.start_node, self.target_node)
        
        # Priority Queue: (f_score, h_score, id, node)
        # h_score is tie breaker (prefer closer to goal), then id
        open_set = [(self.start_node.f_score, self.heuristic(self.start_node, self.target_node), int(self.start_node.id), self.start_node)]
        
        open_set_hash = {self.start_node}

        self.refresh_ui()

        while open_set:
            _, _, _, current = heapq.heappop(open_set)
            open_set_hash.discard(current)

            if current == self.target_node:
                self.reconstruct_path(current)
                self.status_var.set(f"Path Found! Total Cost: {current.g_score}")
                self.header_label.config(text=f"A* Complete! Cost: {current.g_score}")
                self.running_algorithm = False
                self.refresh_ui()
                return

            current.color = THEME["finished_color"]
            if current == self.start_node: current.color = THEME["start_node"] # Keep Start Color
            
            self.refresh_ui()
            time.sleep(0.4)

            neighbors = self._get_neighbors_with_weights(current)
            for neighbor, weight in neighbors:
                if neighbor.color == THEME["finished_color"] and neighbor != self.target_node:
                    continue # Already processed

                tentative_g_score = current.g_score + weight

                if tentative_g_score < neighbor.g_score:
                    # Found better path
                    neighbor.parent = current
                    neighbor.g_score = tentative_g_score
                    neighbor.f_score = tentative_g_score + self.heuristic(neighbor, self.target_node)
                    
                    if neighbor not in open_set_hash:
                        heapq.heappush(open_set, (neighbor.f_score, self.heuristic(neighbor, self.target_node), int(neighbor.id), neighbor))
                        open_set_hash.add(neighbor)
                        if neighbor != self.target_node:
                            neighbor.color = THEME["processing_color"]
                        
                        self.status_var.set(f"Updating Node {neighbor.id} (F: {int(neighbor.f_score)})")
                        self.refresh_ui()
                        time.sleep(0.2)

        self.status_var.set("No Path Found")
        self.header_label.config(text="No Path Found")
        self.running_algorithm = False
        self.refresh_ui()

    def reconstruct_path(self, current):
        path_cost = current.g_score
        while current:
            # Draw path edge? 
            # We can just highlight nodes or draw lines
            if current.parent:
                # Find edge between current and parent
                self.canvas.create_line(current.x, current.y, current.parent.x, current.parent.y, 
                                        width=5, fill=THEME["path_color"])
            current = current.parent

    def _get_neighbors_with_weights(self, node):
        neighbors = []
        for edge in self.edges:
            if edge.source == node: neighbors.append((edge.destination, edge.weight))
            elif edge.destination == node: neighbors.append((edge.source, edge.weight))
        return neighbors

    def refresh_ui(self):
        self.root.after(0, self.draw)

if __name__ == "__main__":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    root = tk.Tk()
    app = AStarApp(root)
    root.mainloop()
