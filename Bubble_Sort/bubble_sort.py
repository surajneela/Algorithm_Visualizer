import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import time
import threading

# Configuration
WIDTH = 800
HEIGHT = 400
DELAY = 0.3  # Speed of animation

# Colors
COLOR_BG = "#ffffff"
COLOR_BAR_DEFAULT = "#007acc"
COLOR_BAR_COMPARE = "#ffd700"   # Gold
COLOR_BAR_SWAP = "#dc3545"      # Red
COLOR_BAR_SORTED = "#28a745"    # Green
COLOR_TEXT = "#000000"

class BubbleSortApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bubble Sort Visualizer")
        self.root.geometry("900x600")
        self.root.configure(bg=COLOR_BG)

        self.data = []
        self.running = False

        self._setup_ui()
        # Prompt immediately at startup
        self.root.after(100, self.prompt_startup_data)

    def _setup_ui(self):
        # Comparison/Status Area
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_label = tk.Label(self.root, textvariable=self.status_var, font=("Segoe UI", 14), bg=COLOR_BG, fg=COLOR_TEXT)
        self.status_label.pack(pady=20)

        # Canvas
        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, bg="#f0f0f0", highlightthickness=0)
        self.canvas.pack(pady=10)

        # Controls
        controls_frame = tk.Frame(self.root, bg=COLOR_BG)
        controls_frame.pack(pady=20)

        btn_style = {"bg": "#333", "fg": "white", "font": ("Segoe UI", 10, "bold"), "relief": "flat", "padx": 15, "pady": 5}

        tk.Button(controls_frame, text="Start Sort", command=self.start_sort, **btn_style).pack(side=tk.LEFT, padx=10)
        tk.Button(controls_frame, text="Enter New Data", command=self.prompt_startup_data, **btn_style).pack(side=tk.LEFT, padx=10)

    def prompt_startup_data(self):
        if self.running: return
        user_input = simpledialog.askstring("Input", "Enter numbers to sort (comma separated):", parent=self.root)
        if user_input:
            self.load_data(user_input)

    def load_data(self, raw_data):
        try:
            new_data = [int(x.strip()) for x in raw_data.split(',')]
            if not new_data: raise ValueError
            self.data = new_data
            self.draw_bars(color_map={})
            self.status_var.set(f"Loaded {len(self.data)} numbers. Ready to sort.")
        except ValueError:
            messagebox.showerror("Error", "Invalid format. Use comma-separated integers.")

    def draw_bars(self, color_map):
        self.canvas.delete("all")
        c_width = WIDTH
        c_height = HEIGHT
        
        if not self.data: return
        
        x_width = c_width / len(self.data)
        offset = 10
        spacing = 5
        max_val = max(self.data) if self.data else 1

        for i, val in enumerate(self.data):
            normalized_h = val / max_val
            
            x0 = i * x_width + offset + spacing
            y0 = c_height - (normalized_h * (c_height - 50))
            x1 = (i + 1) * x_width + offset
            y1 = c_height

            color = color_map.get(i, COLOR_BAR_DEFAULT)
            
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")
            self.canvas.create_text(x0 + (x1-x0)/2, y0 - 15, text=str(val), font=("Segoe UI", 10, "bold"), fill=COLOR_TEXT)

    def start_sort(self):
        if self.running or not self.data: return
        self.running = True
        threading.Thread(target=self.bubble_sort, daemon=True).start()

    def bubble_sort(self):
        n = len(self.data)
        for i in range(n):
            for j in range(0, n - i - 1):
                # Compare j and j+1
                self.status_var.set(f"Comparing index {j} ({self.data[j]}) and {j+1} ({self.data[j+1]})")
                self.update_ui({j: COLOR_BAR_COMPARE, j+1: COLOR_BAR_COMPARE})
                time.sleep(DELAY)

                if self.data[j] > self.data[j+1]:
                    # Swap
                    self.data[j], self.data[j+1] = self.data[j+1], self.data[j]
                    self.status_var.set(f"Swapping {self.data[j+1]} and {self.data[j]}")
                    self.update_ui({j: COLOR_BAR_SWAP, j+1: COLOR_BAR_SWAP})
                    time.sleep(DELAY)
                
                # Reset colors for next step
                self.update_ui({})
            
            # Metric: The element at n-i-1 is now sorted
            # We can visualize this if we want, or just wait for end to show all sorted?
            # A common way is to keep 'sorted' ones green.
            # But the draw_bars logic simply redraws every frame. 
            # I won't complicate draw_bars with persistent state, but I can pass a list of sorted indices if I stored them.
            # Simplified: just finish loop.
        
        self.status_var.set("Sorting Complete!")
        self.update_ui({i: COLOR_BAR_SORTED for i in range(n)})
        self.running = False

    def update_ui(self, color_map):
        self.root.after(0, lambda: self.draw_bars(color_map))

if __name__ == "__main__":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
        
    root = tk.Tk()
    app = BubbleSortApp(root)
    root.mainloop()
