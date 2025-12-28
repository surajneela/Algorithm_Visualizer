import tkinter as tk
import random
import threading
import time
import heapq

# Configuration
CELL_SIZE = 25
COLS = 30
ROWS = 25
WIDTH = COLS * CELL_SIZE
HEIGHT = ROWS * CELL_SIZE

# Colors
COLOR_WALL = "#000000"       # Black
COLOR_PATH = "#ffffff"       # White (Cost 1)
COLOR_MUD = "#8b4513"        # SaddleBrown (Cost 5)
COLOR_START = "#00ff00"      # Green
COLOR_END = "#ff0000"        # Red
COLOR_VISITED = "#add8e6"    # Light Blue
COLOR_PATH_FINAL = "#ffff00" # Yellow for the solution path
COLOR_BG = "#f0f0f0"

class DijkstraMazeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dijkstra Maze Solver (Weighted)")
        self.root.geometry(f"{WIDTH + 50}x{HEIGHT + 150}")
        self.root.configure(bg=COLOR_BG)

        # 0 = Path, 1 = Wall, 5 = Mud
        self.grid = [] 
        self.start = (0, 0)
        self.end = (ROWS - 1, COLS - 1)
        self.running = False

        self._setup_ui()
        self.generate_maze()

    def _setup_ui(self):
        # Header
        self.header_frame = tk.Frame(self.root, bg=COLOR_BG, pady=10)
        self.header_frame.pack(side=tk.TOP, fill=tk.X)
        
        self.header_label = tk.Label(self.header_frame, text="Dijkstra Maze (Mud Cost = 5)", bg=COLOR_BG, font=("Segoe UI", 12, "bold"))
        self.header_label.pack()

        # Controls
        self.controls_frame = tk.Frame(self.root, bg=COLOR_BG, pady=5)
        self.controls_frame.pack(side=tk.TOP, fill=tk.X)

        btn_style = {"bg": "#007acc", "fg": "white", "font": ("Segoe UI", 9, "bold"), "relief": "flat", "padx": 10}
        
        tk.Button(self.controls_frame, text="Generate Maze", command=self.generate_maze_thread, **btn_style).pack(side=tk.LEFT, padx=5)
        tk.Button(self.controls_frame, text="Add Random Mud", command=self.add_mud, **btn_style).pack(side=tk.LEFT, padx=5)
        tk.Button(self.controls_frame, text="Run Dijkstra", command=self.run_dijkstra, **btn_style).pack(side=tk.LEFT, padx=5)
        tk.Button(self.controls_frame, text="Reset Visuals", command=self.reset_visuals, **btn_style).pack(side=tk.LEFT, padx=5)

        # Canvas
        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, bg=COLOR_WALL, highlightthickness=0)
        self.canvas.pack(pady=10)
        
        # Click handler
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_click)

    def on_click(self, event):
        if self.running: return
        c = event.x // CELL_SIZE
        r = event.y // CELL_SIZE
        
        if 0 <= r < ROWS and 0 <= c < COLS:
            # Toggle Wall/Path/Mud cycle? Or just toggle Wall/Path manually.
            # Let's make manual click toggling Wall <-> Path for simplicity
            # Use "Add Mud" button for Mud
            if (r, c) == self.start or (r, c) == self.end: return
            
            if self.grid[r][c] == 1:
                self.grid[r][c] = 0
                self.draw_cell(r, c, COLOR_PATH)
            else:
                self.grid[r][c] = 1
                self.draw_cell(r, c, COLOR_WALL)

    def reset_visuals(self):
        if self.running: return
        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")
        for r in range(ROWS):
            for c in range(COLS):
                color = COLOR_PATH
                if self.grid[r][c] == 1: color = COLOR_WALL
                elif self.grid[r][c] == 5: color = COLOR_MUD
                self.draw_cell(r, c, color)
        
        self.draw_cell(self.start[0], self.start[1], COLOR_START)
        self.draw_cell(self.end[0], self.end[1], COLOR_END)

    def draw_cell(self, r, c, color):
        x1 = c * CELL_SIZE
        y1 = r * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

    def generate_maze_thread(self):
        if self.running: return
        self.running = True
        threading.Thread(target=self._generate_maze_logic, daemon=True).start()

    def generate_maze(self):
        self.grid = [[1 for _ in range(COLS)] for _ in range(ROWS)]
        
        # DFS Backtracker for generation
        stack = []
        self.grid[0][0] = 0
        stack.append((0, 0))

        while stack:
            r, c = stack[-1]
            neighbors = []
            directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]
            
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < ROWS and 0 <= nc < COLS and self.grid[nr][nc] == 1:
                    neighbors.append((nr, nc, dr, dc))
            
            if neighbors:
                nr, nc, dr, dc = random.choice(neighbors)
                wr, wc = r + dr//2, c + dc//2
                self.grid[wr][wc] = 0
                self.grid[nr][nc] = 0
                stack.append((nr, nc))
            else:
                stack.pop()
        
        # Ensure end accessible
        self.grid[ROWS-1][COLS-1] = 0
        self.grid[ROWS-2][COLS-1] = 0 
        self.grid[ROWS-1][COLS-2] = 0

        self.root.after(0, self.draw_grid)
        self.running = False

    def _generate_maze_logic(self):
        self.generate_maze()

    def add_mud(self):
        if self.running: return
        # Randomly turn 20% of path cells into Mud
        for r in range(ROWS):
            for c in range(COLS):
                if self.grid[r][c] == 0 and (r, c) != self.start and (r, c) != self.end:
                    if random.random() < 0.2:
                        self.grid[r][c] = 5 # Weight 5
        self.draw_grid()

    def run_dijkstra(self):
        if self.running: return
        self.running = True
        self.reset_visuals() # Clear old path
        threading.Thread(target=self._dijkstra_logic, daemon=True).start()

    def _dijkstra_logic(self):
        # Priority Queue: (cost, r, c, path_list)
        pq = [(0, self.start[0], self.start[1], [self.start])]
        
        # Distances
        costs = {self.start: 0}
        visited = set()

        while pq:
            cost, r, c, path = heapq.heappop(pq)
            
            if (r, c) in visited: continue
            visited.add((r, c))

            if (r, c) == self.end:
                self.highlight_path(path)
                final_cost = costs[(r, c)]
                self.header_label.config(text=f"Path Found! Total Cost: {final_cost}")
                self.running = False
                return

            if (r, c) != self.start:
                # visualize visit
                if self.grid[r][c] == 5:
                    self.color_cell_thread(r, c, "#a0522d") # Visited Mud (Slightly lighter brown?) or just blue
                else:
                    self.color_cell_thread(r, c, COLOR_VISITED)
                time.sleep(0.005)

            # Neighbors
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < ROWS and 0 <= nc < COLS:
                    cell_type = self.grid[nr][nc]
                    if cell_type != 1: # Not Wall
                        weight = 1 if cell_type == 0 else 5
                        new_cost = cost + weight
                        
                        if new_cost < costs.get((nr, nc), float('inf')):
                            costs[(nr, nc)] = new_cost
                            new_path = list(path)
                            new_path.append((nr, nc))
                            heapq.heappush(pq, (new_cost, nr, nc, new_path))
        
        self.running = False

    def color_cell_thread(self, r, c, color):
        self.root.after(0, lambda: self.draw_cell(r, c, color))

    def highlight_path(self, path):
        for r, c in path:
            if (r, c) != self.start and (r, c) != self.end:
                self.color_cell_thread(r, c, COLOR_PATH_FINAL)
            time.sleep(0.01)

if __name__ == "__main__":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    root = tk.Tk()
    app = DijkstraMazeApp(root)
    root.mainloop()
