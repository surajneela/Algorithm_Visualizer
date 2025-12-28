import tkinter as tk
from tkinter import messagebox
import random
import time
import threading

# Configuration
WIDTH = 800
HEIGHT = 400
BAR_WIDTH = 20
DELAY = 0.5  # Seconds between steps

# Colors
COLOR_BG = "#ffffff"
COLOR_BAR_DEFAULT = "#007acc"
COLOR_BAR_CHECKING = "#ffd700"  # Gold
COLOR_BAR_FOUND = "#28a745"     # Green
COLOR_BAR_NOT_FOUND = "#dc3545" # Red
COLOR_TEXT = "#000000"

class LinearSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Linear Search Visualizer")
        self.root.geometry("900x600")
        self.root.configure(bg=COLOR_BG)

        self.data = []
        self.bars = []
        self.running = False
        self.target = None

        self._setup_ui()
        self.generate_data()

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

        tk.Label(controls_frame, text="Target Value:", bg=COLOR_BG, font=("Segoe UI", 12)).pack(side=tk.LEFT, padx=5)
        
        self.target_entry = tk.Entry(controls_frame, font=("Segoe UI", 12), width=10)
        self.target_entry.pack(side=tk.LEFT, padx=5)

        btn_style = {"bg": "#333", "fg": "white", "font": ("Segoe UI", 10, "bold"), "relief": "flat", "padx": 15, "pady": 5}

        tk.Button(controls_frame, text="Search", command=self.start_search, **btn_style).pack(side=tk.LEFT, padx=10)
        tk.Button(controls_frame, text="New Array", command=self.generate_data, **btn_style).pack(side=tk.LEFT, padx=10)

    def generate_data(self):
        if self.running: return
        self.data = [random.randint(10, 100) for _ in range(20)]
        self.draw_bars(color_map={})
        self.status_var.set("New Array Generated")

    def draw_bars(self, color_map):
        self.canvas.delete("all")
        c_width = WIDTH
        c_height = HEIGHT
        
        x_width = c_width / len(self.data)
        offset = 10
        spacing = 5
        
        normalized_data = [i / max(self.data) for i in self.data]

        for i, height in enumerate(normalized_data):
            x0 = i * x_width + offset + spacing
            y0 = c_height - (height * (c_height - 50))
            x1 = (i + 1) * x_width + offset
            y1 = c_height

            val = self.data[i]
            color = color_map.get(i, COLOR_BAR_DEFAULT)
            
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")
            self.canvas.create_text(x0 + (x1-x0)/2, y0 - 15, text=str(val), font=("Segoe UI", 10, "bold"), fill=COLOR_TEXT)

    def start_search(self):
        if self.running: return
        target_str = self.target_entry.get()
        if not target_str.isdigit():
            messagebox.showerror("Error", "Please enter a valid integer")
            return
        
        self.target = int(target_str)
        self.running = True
        threading.Thread(target=self.linear_search, daemon=True).start()

    def linear_search(self):
        for i, val in enumerate(self.data):
            self.status_var.set(f"Checking index {i}: Is {val} == {self.target}?")
            
            # Highlight checking
            self.update_ui({i: COLOR_BAR_CHECKING})
            time.sleep(DELAY)

            if val == self.target:
                self.status_var.set(f"Found {self.target} at index {i}!")
                self.update_ui({i: COLOR_BAR_FOUND})
                self.running = False
                return

        self.status_var.set(f"Value {self.target} not found in array.")
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
    app = LinearSearchApp(root)
    root.mainloop()
