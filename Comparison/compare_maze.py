"""Compare pathfinding algorithms: Dijkstra vs A*.

Creates a side-by-side race visualization to compare the
exploration behavior and speed of Dijkstra and A* on the
same randomly generated maze.
"""

import tkinter as tk
import time
import threading
import heapq
import random

# Configuration
CELL_SIZE = 15
COLS = 20
ROWS = 20
WIDTH = COLS * CELL_SIZE
HEIGHT = ROWS * CELL_SIZE

# Colors
COLOR_WALL = "#000000"
COLOR_PATH = "#ffffff"
COLOR_MUD = "#8b4513"
COLOR_START = "#00ff00"
COLOR_END = "#ff0000"
COLOR_VISITED_DIJKSTRA = "#2196F3" # Blue
COLOR_VISITED_ASTAR = "#9C27B0"    # Purple
COLOR_PATH_FINAL = "#ffff00"
COLOR_BG = "#f0f0f0"

class CompareApp:
    """Application that runs a simultaneous comparison of two algorithms.

    The app generates a shared maze and visualizes Dijkstra (left)
    and A* (right) exploring the grid and tracing their final paths.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Race: Dijkstra vs A*")
        self.root.geometry(f"{WIDTH*2 + 80}x{HEIGHT + 200}")
        self.root.configure(bg=COLOR_BG)

        self.grid_map = [] # Shared map data (0=Path, 1=Wall, 5=Mud)
        self.start = (0,0)
        self.end = (ROWS-1, COLS-1)
        self.running = False

        self._setup_ui()
        self.generate_maze()

    def _setup_ui(self):
        # Header
        tk.Label(self.root, text="Algorithm Race", font=("Segoe UI", 16, "bold"), bg=COLOR_BG).pack(pady=5)
        
        # Stats Frame
        stats_frame = tk.Frame(self.root, bg=COLOR_BG)
        stats_frame.pack(fill=tk.X, padx=20)
        
        self.lbl_dijkstra = tk.Label(stats_frame, text="Dijkstra: Ready", font=("Consolas", 11), bg=COLOR_BG, fg="blue")
        self.lbl_dijkstra.pack(side=tk.LEFT, expand=True)
        
        self.lbl_astar = tk.Label(stats_frame, text="A*: Ready", font=("Consolas", 11), bg=COLOR_BG, fg="purple")
        self.lbl_astar.pack(side=tk.RIGHT, expand=True)

        # Canvas Frame (Side by Side)
        canvas_frame = tk.Frame(self.root, bg=COLOR_BG)
        canvas_frame.pack(pady=10)

        # Left: Dijkstra
        frame_l = tk.Frame(canvas_frame, bg=COLOR_BG)
        frame_l.pack(side=tk.LEFT, padx=10)
        tk.Label(frame_l, text="Dijkstra (Blind Search)", bg=COLOR_BG).pack()
        self.c_dijkstra = tk.Canvas(frame_l, width=WIDTH, height=HEIGHT, bg="black", highlightthickness=0)
        self.c_dijkstra.pack()

        # Right: A*
        frame_r = tk.Frame(canvas_frame, bg=COLOR_BG)
        frame_r.pack(side=tk.LEFT, padx=10)
        tk.Label(frame_r, text="A* (Heuristic Search)", bg=COLOR_BG).pack()
        self.c_astar = tk.Canvas(frame_r, width=WIDTH, height=HEIGHT, bg="black", highlightthickness=0)
        self.c_astar.pack()

        # Controls
        ctrl_frame = tk.Frame(self.root, bg=COLOR_BG)
        ctrl_frame.pack(pady=10)
        
        btn_style = {"relief": "flat", "bg": "#333", "fg": "white", "font": ("Segoe UI", 10, "bold"), "padx": 15}
        tk.Button(ctrl_frame, text="Generate Maze", command=self.generate_maze, **btn_style).pack(side=tk.LEFT, padx=5)
        tk.Button(ctrl_frame, text="Add Mud", command=self.add_mud, **btn_style).pack(side=tk.LEFT, padx=5)
        tk.Button(ctrl_frame, text="START RACE", command=self.start_race, bg="#007acc", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", padx=15).pack(side=tk.LEFT, padx=5)

    def draw_grid(self, canvas):
        canvas.delete("all")
        for r in range(ROWS):
            for c in range(COLS):
                color = COLOR_PATH
                if self.grid_map[r][c] == 1: color = COLOR_WALL
                elif self.grid_map[r][c] == 5: color = COLOR_MUD
                
                x1, y1 = c*CELL_SIZE, r*CELL_SIZE
                canvas.create_rectangle(x1, y1, x1+CELL_SIZE, y1+CELL_SIZE, fill=color, outline="")
        
        # Start/End
        self.draw_cell(canvas, self.start[0], self.start[1], COLOR_START)
        self.draw_cell(canvas, self.end[0], self.end[1], COLOR_END)

    def draw_cell(self, canvas, r, c, color):
        x1, y1 = c*CELL_SIZE, r*CELL_SIZE
        canvas.create_rectangle(x1, y1, x1+CELL_SIZE, y1+CELL_SIZE, fill=color, outline="")

    def generate_maze(self):
        if self.running: return
        self.grid_map = [[1 for _ in range(COLS)] for _ in range(ROWS)]
        
        # Simple DFS Maze
        stack = [(0,0)]
        self.grid_map[0][0] = 0
        visited = set([(0,0)])
        
        while stack:
            r, c = stack[-1]
            neighbors = []
            for dr, dc in [(-2,0), (2,0), (0,-2), (0,2)]:
                nr, nc = r+dr, c+dc
                if 0 <= nr < ROWS and 0 <= nc < COLS and self.grid_map[nr][nc] == 1:
                    neighbors.append((nr,nc,dr,dc))
            
            if neighbors:
                nr, nc, dr, dc = random.choice(neighbors)
                self.grid_map[r+dr//2][c+dc//2] = 0
                self.grid_map[nr][nc] = 0
                stack.append((nr,nc))
            else:
                stack.pop()
        
        self.grid_map[ROWS-1][COLS-1] = 0
        self.grid_map[ROWS-2][COLS-1] = 0
        
        self.draw_grid(self.c_dijkstra)
        self.draw_grid(self.c_astar)
        self.lbl_dijkstra.config(text="Dijkstra: Ready")
        self.lbl_astar.config(text="A*: Ready")

    def add_mud(self):
        if self.running: return
        for r in range(ROWS):
            for c in range(COLS):
                if self.grid_map[r][c] == 0 and random.random() < 0.1:
                    self.grid_map[r][c] = 5
        self.draw_grid(self.c_dijkstra)
        self.draw_grid(self.c_astar)

    def start_race(self):
        if self.running: return
        self.running = True
        
        # Reset visual state only (not the map)
        self.draw_grid(self.c_dijkstra)
        self.draw_grid(self.c_astar)

        t1 = threading.Thread(target=self.run_dijkstra, daemon=True)
        t2 = threading.Thread(target=self.run_astar, daemon=True)
        t1.start()
        t2.start()
        
        # Monitor threads
        threading.Thread(target=self.monitor_race, args=(t1, t2), daemon=True).start()

    def monitor_race(self, t1, t2):
        t1.join()
        t2.join()
        self.running = False

    # --- Dijkstra ---
    def run_dijkstra(self):
        pq = [(0, self.start)]
        costs = {self.start: 0}
        visited_count = 0
        parents = {self.start: None}
        
        while pq:
            cost, (r, c) = heapq.heappop(pq)
            
            if (r,c) == self.end:
                self.trace_path(self.c_dijkstra, parents)
                self.lbl_dijkstra.config(text=f"Dijkstra: Done! Visited: {visited_count}")
                return

            if (r,c) != self.start:
                visited_count += 1
                self.root.after(0, lambda rr=r, cc=c: self.draw_cell(self.c_dijkstra, rr, cc, COLOR_VISITED_DIJKSTRA))
                self.lbl_dijkstra.config(text=f"Dijkstra: Visiting... {visited_count}")
                time.sleep(0.01) # Slow down to see race
            
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = r+dr, c+dc
                if 0 <= nr < ROWS and 0 <= nc < COLS and self.grid_map[nr][nc] != 1:
                    weight = 5 if self.grid_map[nr][nc] == 5 else 1
                    new_cost = cost + weight
                    
                    if new_cost < costs.get((nr,nc), float('inf')):
                        costs[(nr,nc)] = new_cost
                        parents[(nr,nc)] = (r,c)
                        heapq.heappush(pq, (new_cost, (nr,nc)))

    # --- A* ---
    def run_astar(self):
        def h(r, c): return abs(r-self.end[0]) + abs(c-self.end[1])
        
        pq = [(0, 0, self.start)] # (f, h, pos)
        g_costs = {self.start: 0}
        visited_count = 0
        parents = {self.start: None}

        while pq:
            f, _, (r, c) = heapq.heappop(pq)
            
            if (r,c) == self.end:
                self.trace_path(self.c_astar, parents)
                self.lbl_astar.config(text=f"A*: Done! Visited: {visited_count}")
                return

            if (r,c) != self.start:
                visited_count += 1
                self.root.after(0, lambda rr=r, cc=c: self.draw_cell(self.c_astar, rr, cc, COLOR_VISITED_ASTAR))
                self.lbl_astar.config(text=f"A*: Visiting... {visited_count}")
                time.sleep(0.01)

            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = r+dr, c+dc
                if 0 <= nr < ROWS and 0 <= nc < COLS and self.grid_map[nr][nc] != 1:
                    weight = 5 if self.grid_map[nr][nc] == 5 else 1
                    new_g = g_costs.get((r,c)) + weight
                    
                    if new_g < g_costs.get((nr,nc), float('inf')):
                        g_costs[(nr,nc)] = new_g
                        parents[(nr,nc)] = (r,c)
                        new_h = h(nr, nc)
                        heapq.heappush(pq, (new_g + new_h, new_h, (nr,nc)))

    def trace_path(self, canvas, parents):
        curr = self.end
        while curr:
            if curr != self.start and curr != self.end:
                r, c = curr
                self.root.after(0, lambda rr=r, cc=c, cv=canvas: self.draw_cell(cv, rr, cc, COLOR_PATH_FINAL))
            curr = parents.get(curr)
            time.sleep(0.01)

if __name__ == "__main__":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    root = tk.Tk()
    app = CompareApp(root)
    root.mainloop()
