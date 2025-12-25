import tkinter as tk
import random
import threading
import time
from collections import deque

# Configuration
CELL_SIZE = 25
COLS = 25
ROWS = 25
WIDTH = COLS * CELL_SIZE
HEIGHT = ROWS * CELL_SIZE

# Colors
COLOR_WALL = "#000000"       # Black
COLOR_PATH = "#ffffff"       # White
COLOR_START = "#00ff00"      # Green
COLOR_END = "#ff0000"        # Red
COLOR_VISITED = "#add8e6"    # Light Blue
COLOR_PATH_FINAL = "#ffff00" # Yellow for the solution path
COLOR_BG = "#f0f0f0"

class MazeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Maze Generator & Solver")
        self.root.geometry(f"{WIDTH + 50}x{HEIGHT + 100}")
        self.root.configure(bg=COLOR_BG)

        self.grid = [] # 2D array: 1 = Wall, 0 = Path
        self.start = (0, 0)
        self.end = (ROWS - 1, COLS - 1)
        self.running = False

        self._setup_ui()
        self.generate_maze()

    def _setup_ui(self):
        # Controls Header
        self.controls_frame = tk.Frame(self.root, bg=COLOR_BG, pady=10)
        self.controls_frame.pack(side=tk.TOP, fill=tk.X)

        btn_style = {"bg": "#007acc", "fg": "white", "font": ("Segoe UI", 10, "bold"), "relief": "flat", "padx": 10}
        
        tk.Button(self.controls_frame, text="Generate Maze", command=self.generate_maze_thread, **btn_style).pack(side=tk.LEFT, padx=10)
        tk.Button(self.controls_frame, text="Start BFS", command=lambda: self.run_search("BFS"), **btn_style).pack(side=tk.LEFT, padx=10)
        tk.Button(self.controls_frame, text="Start DFS", command=lambda: self.run_search("DFS"), **btn_style).pack(side=tk.LEFT, padx=10)
        tk.Button(self.controls_frame, text="Compare BFS & DFS", command=self.open_compare_window, **btn_style).pack(side=tk.LEFT, padx=10)
        tk.Button(self.controls_frame, text="Reset", command=self.reset_visuals, **btn_style).pack(side=tk.LEFT, padx=10)
        tk.Label(self.controls_frame, text="Map Visualizer", bg=COLOR_BG, font=("Segoe UI", 12, "bold")).pack(side=tk.RIGHT, padx=20)

        # Canvas
        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, bg=COLOR_WALL, highlightthickness=0)
        self.canvas.pack(pady=10)

    def reset_visuals(self):
        if self.running: return
        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")
        self._draw_grid_on_canvas(self.canvas)

    def _draw_grid_on_canvas(self, canvas):
        for r in range(ROWS):
            for c in range(COLS):
                color = COLOR_WALL if self.grid[r][c] == 1 else COLOR_PATH
                self._draw_cell_on_canvas(canvas, r, c, color)
        
        # Draw Start/End
        self._draw_cell_on_canvas(canvas, self.start[0], self.start[1], COLOR_START)
        self._draw_cell_on_canvas(canvas, self.end[0], self.end[1], COLOR_END)

    def draw_cell(self, r, c, color):
        self._draw_cell_on_canvas(self.canvas, r, c, color)

    def _draw_cell_on_canvas(self, canvas, r, c, color):
        x1 = c * CELL_SIZE
        y1 = r * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

    def generate_maze_thread(self):
        if self.running: return
        self.running = True
        threading.Thread(target=self._generate_maze_logic, daemon=True).start()

    def generate_maze(self):
        # Initialize grid with walls
        self.grid = [[1 for _ in range(COLS)] for _ in range(ROWS)]
        
        # Iterative Randomized Prim's / DFS for maze generation
        # Let's use DFS Backtracker for nice long corridors
        stack = []
        start_cell = (0, 0)
        self.grid[0][0] = 0
        stack.append(start_cell)

        while stack:
            r, c = stack[-1]
            
            # Find unvisited neighbors (distance 2 away)
            neighbors = []
            directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]
            
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < ROWS and 0 <= nc < COLS and self.grid[nr][nc] == 1:
                    neighbors.append((nr, nc, dr, dc))
            
            if neighbors:
                nr, nc, dr, dc = random.choice(neighbors)
                # Knock down wall between
                wr, wc = r + dr//2, c + dc//2
                self.grid[wr][wc] = 0
                self.grid[nr][nc] = 0
                stack.append((nr, nc))
            else:
                stack.pop()
        
        # Ensure end is accessible (sometimes basic algo leaves it walled if COLS/ROWS are even)
        self.grid[ROWS-1][COLS-1] = 0
        self.grid[ROWS-2][COLS-1] = 0 
        self.grid[ROWS-1][COLS-2] = 0

        self.root.after(0, self.draw_grid)
        self.running = False


    def _generate_maze_logic(self):
        # Thread wrapper if we wanted animation, currently instant for speed
        self.generate_maze()

    def run_search(self, algo_type):
        if self.running: return
        self.running = True
        # Redraw to clear previous paths
        self.draw_grid()
        
        threading.Thread(target=self._solve_logic, args=(algo_type, self.canvas, self._on_search_complete), daemon=True).start()
    
    def _on_search_complete(self):
        self.running = False

    def open_compare_window(self):
        if self.running: return
        CompareWindow(self.root, self.grid, self.start, self.end, self.draw_cell, self._solve_logic)

    def _solve_logic(self, algo_type, target_canvas, on_complete=None):
        q = deque() if algo_type == "BFS" else [] # Stack for DFS
        q.append((self.start, [self.start]))
        visited = set()
        visited.add(self.start)

        while q:
            if algo_type == "BFS":
                (r, c), path = q.popleft()
            else:
                try:
                    (r, c), path = q.pop()
                except IndexError: break # Stack empty

            if (r, c) == self.end:
                self.highlight_path(path, target_canvas)
                if on_complete: on_complete()
                return

            if (r, c) != self.start:
                self.color_cell_thread(r, c, COLOR_VISITED, target_canvas)
                time.sleep(0.015) # Speed of animation

            neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            if algo_type == "DFS": random.shuffle(neighbors)

            for dr, dc in neighbors:
                nr, nc = r + dr, c + dc
                if 0 <= nr < ROWS and 0 <= nc < COLS:
                    if self.grid[nr][nc] == 0 and (nr, nc) not in visited:
                        visited.add((nr, nc))
                        new_path = list(path)
                        new_path.append((nr, nc))
                        q.append(((nr, nc), new_path))
        
        if on_complete: on_complete()

    def color_cell_thread(self, r, c, color, canvas):
        try:
            self.root.after(0, lambda: self._draw_cell_on_canvas(canvas, r, c, color))
        except: pass

    def highlight_path(self, path, canvas):
        for r, c in path:
            if (r, c) != self.start and (r, c) != self.end:
                self.color_cell_thread(r, c, COLOR_PATH_FINAL, canvas)
            time.sleep(0.01)

class CompareWindow:
    def __init__(self, master, grid, start, end, draw_func, solve_func):
        self.top = tk.Toplevel(master)
        self.top.title("BFS vs DFS Comparison")
        self.top.geometry(f"{WIDTH*2 + 80}x{HEIGHT + 100}")
        self.top.configure(bg=COLOR_BG)
        
        self.grid = grid
        self.start = start
        self.end = end
        
        # Reuse logic from main app (hacky but effective for simple script)
        # We need a reference to the main app instance methods if they were static, but they are instance.
        # So we reimplement or link? 
        # Easier: Duplicate mini logic or pass methods. Passed methods `solve_func`.
        # solve_func requires `self` usually if it's bound.
        # Let's clean up: The Main App methods `_solve_logic` rely on `self.grid`. 
        # Since I passed `_solve_logic` (bound method), it will use Main App's grid.
        # This is fine since grids are identical.
        
        self.solve_func = solve_func
        
        # Layout
        frame = tk.Frame(self.top, bg=COLOR_BG)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left (BFS)
        self.lbl_bfs = tk.Label(frame, text="Breadth-First Search (BFS)", bg=COLOR_BG, font=("Segoe UI", 12, "bold"))
        self.lbl_bfs.grid(row=0, column=0)
        self.canvas_bfs = tk.Canvas(frame, width=WIDTH, height=HEIGHT, bg=COLOR_WALL, highlightthickness=0)
        self.canvas_bfs.grid(row=1, column=0, padx=10)
        
        # Right (DFS)
        self.lbl_dfs = tk.Label(frame, text="Depth-First Search (DFS)", bg=COLOR_BG, font=("Segoe UI", 12, "bold"))
        self.lbl_dfs.grid(row=0, column=1)
        self.canvas_dfs = tk.Canvas(frame, width=WIDTH, height=HEIGHT, bg=COLOR_WALL, highlightthickness=0)
        self.canvas_dfs.grid(row=1, column=1, padx=10)
        
        # Draw Initial Grids
        self.draw_initial(self.canvas_bfs)
        self.draw_initial(self.canvas_dfs)
        
        # Start Race
        self.start_race()

    def draw_initial(self, canvas):
        # We need to draw the main grid onto these canvases
        # Can't use main app draw_grid cause it targets self.canvas
        # We'll use the _draw_cell_on_canvas if we can access it or just manual loop
        for r in range(ROWS):
            for c in range(COLS):
                color = COLOR_WALL if self.grid[r][c] == 1 else COLOR_PATH
                x1, y1 = c * CELL_SIZE, r * CELL_SIZE
                canvas.create_rectangle(x1, y1, x1+CELL_SIZE, y1+CELL_SIZE, fill=color, outline="")
        
        # Start/End
        sx, sy = self.start[1]*CELL_SIZE, self.start[0]*CELL_SIZE
        canvas.create_rectangle(sx, sy, sx+CELL_SIZE, sy+CELL_SIZE, fill=COLOR_START, outline="")
        ex, ey = self.end[1]*CELL_SIZE, self.end[0]*CELL_SIZE
        canvas.create_rectangle(ex, ey, ex+CELL_SIZE, ey+CELL_SIZE, fill=COLOR_END, outline="")

    def start_race(self):
        # Run both in threads
        threading.Thread(target=self.solve_func, args=("BFS", self.canvas_bfs), daemon=True).start()
        threading.Thread(target=self.solve_func, args=("DFS", self.canvas_dfs), daemon=True).start()


if __name__ == "__main__":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    root = tk.Tk()
    app = MazeApp(root)
    root.mainloop()
