import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
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
    "processing_color": "#ffd700",   # Gold
    "finished_color": "#98fb98",     # Pale Green
    "path_color": "#ff4500",         # Orange Red for final path
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
        self.visited = False
        self.distance = float('inf') # For Dijkstra
        self.radius = 24

class Edge:
    def __init__(self, source, destination, weight=1):
        self.source = source
        self.destination = destination
        self.weight = weight

class DijkstraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dijkstra's Algorithm Visualizer")
        self.root.geometry("1000x700")
        self.root.configure(bg=THEME["bg_color"])

        self.nodes = []
        self.edges = []
        self.selected_node = None
        self.running_algorithm = False

        self._setup_ui()

    def _setup_ui(self):
        # Header
        self.header_label = tk.Label(self.root, text="Dijkstra's Visualizer (Weighted Graph)", 
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

        # Controls
        self.controls_panel = tk.Frame(self.root, bg=THEME["bg_color"], pady=20)
        self.controls_panel.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_var = tk.StringVar()
        self.status_var.set("Click to add nodes. Drag connect to add Edges. Right-Click to Reset.")
        tk.Label(self.controls_panel, textvariable=self.status_var, bg=THEME["bg_color"], font=("Consolas", 11)).pack(pady=(0, 10))

        btn_frame = tk.Frame(self.controls_panel, bg=THEME["bg_color"])
        btn_frame.pack()

        self.create_button(btn_frame, "Run Dijkstra", self.run_dijkstra, bg=THEME["accent_color"])
        self.create_button(btn_frame, "Clear Graph", self.clear_graph, bg="#d9534f")

    def create_button(self, parent, text, command, bg):
        tk.Button(parent, text=text, command=command, bg=bg, fg="white", 
                  relief="flat", padx=20, pady=8, font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=10)

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
                self.status_var.set(f"Selected Node {clicked_node.id}. Click another to connect.")
            else:
                if self.selected_node != clicked_node:
                    self.prompt_edge_weight(self.selected_node, clicked_node)
                self.selected_node = None
        else:
            self.add_node(event.x, event.y)
        
        self.drag_node = None
        self.draw()

    def prompt_edge_weight(self, u, v):
        weight = simpledialog.askinteger("Edge Weight", f"Enter weight for edge {u.id}-{v.id}:", 
                                       parent=self.root, minvalue=1, initialvalue=1)
        if weight is None: weight = 1 # Default if cancelled
        self.add_edge(u, v, weight)
        self.status_var.set(f"Added Edge {u.id}-{v.id} (Weight: {weight})")

    def add_node(self, x, y):
        node = Node(len(self.nodes), x, y)
        self.nodes.append(node)

    def add_edge(self, u, v, weight):
        # Remove existing if any
        self.edges = [e for e in self.edges if not ((e.source==u and e.destination==v) or (e.source==v and e.destination==u))]
        self.edges.append(Edge(u, v, weight))

    def clear_graph(self):
        if self.running_algorithm: return
        self.nodes = []
        self.edges = []
        self.selected_node = None
        self.status_var.set("Graph Cleared")
        self.draw()

    def draw(self):
        self.canvas.delete("all")

        # Edges
        for edge in self.edges:
            # Line
            self.canvas.create_line(edge.source.x, edge.source.y, edge.destination.x, edge.destination.y, 
                                    width=2, fill=THEME["edge_color"])
            
            # Weight Label (Midpoint)
            mx, my = (edge.source.x + edge.destination.x)/2, (edge.source.y + edge.destination.y)/2
            self.canvas.create_oval(mx-10, my-10, mx+10, my+10, fill="white", outline=THEME["edge_color"])
            self.canvas.create_text(mx, my, text=str(edge.weight), font=THEME["font_edge"])

        # Nodes
        for node in self.nodes:
            # Highlight Selection
            if node == self.selected_node:
                self.canvas.create_oval(node.x - node.radius - 3, node.y - node.radius - 3,
                                        node.x + node.radius + 3, node.y + node.radius + 3,
                                        outline=THEME["accent_color"], width=3)
            
            self.canvas.create_oval(node.x - node.radius, node.y - node.radius,
                                    node.x + node.radius, node.y + node.radius,
                                    fill=node.color, outline=THEME["node_outline"])
            
            # Text: ID and Distance
            label = node.id
            if node.distance != float('inf'):
                label += f"\n({node.distance})"
            
            self.canvas.create_text(node.x, node.y, text=label, fill=THEME["text_color"], font=THEME["font_node"])

    # --- Dijkstra Algorithm ---
    def run_dijkstra(self):
        if self.running_algorithm or not self.nodes: return
        
        # Assume start node is the first one or selected one
        start_node = self.selected_node if self.selected_node else self.nodes[0]
        
        self.running_algorithm = True
        self.status_var.set(f"Running Dijkstra from Node {start_node.id}...")
        threading.Thread(target=self._dijkstra_logic, args=(start_node,), daemon=True).start()

    def _dijkstra_logic(self, start_node):
        # Reset
        for n in self.nodes:
            n.distance = float('inf')
            n.visited = False
            n.color = THEME["node_fill"]
        
        start_node.distance = 0
        pq = [(0, int(start_node.id), start_node)] # (dist, id_tiebreaker, node_obj)
        
        self.refresh_ui()

        while pq:
            d, _, current = heapq.heappop(pq)
            
            if current.visited: continue
            current.visited = True
            current.color = THEME["finished_color"]
            self.status_var.set(f"Visited Node {current.id}. Distance: {d}")
            self.refresh_ui()
            time.sleep(0.5)

            # Neighbors
            neighbors = self._get_neighbors_with_weights(current)
            for neighbor, weight in neighbors:
                if not neighbor.visited:
                    new_dist = d + weight
                    if new_dist < neighbor.distance:
                        neighbor.distance = new_dist
                        neighbor.color = THEME["processing_color"] # Highlight being updated
                        heapq.heappush(pq, (new_dist, int(neighbor.id), neighbor))
                        self.status_var.set(f"Updated Node {neighbor.id} distance to {new_dist}")
                        self.refresh_ui()
                        time.sleep(0.3)
                        neighbor.color = THEME["node_fill"] # Reset color after update
        
        self.running_algorithm = False
        self.status_var.set("Dijkstra Complete!")
        self.refresh_ui()

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
    app = DijkstraApp(root)
    root.mainloop()
