import tkinter as tk
from tkinter import messagebox
import random
import time
import threading

# Configuration
WIDTH = 800
HEIGHT = 400
DELAY = 1.0  # Slower for binary search to see steps clearly

# Colors
COLOR_BG = "#ffffff"
COLOR_BAR_DEFAULT = "#007acc"
COLOR_BAR_ACTIVE_RANGE = "#90e0ef" # Light blue for current range
COLOR_BAR_MID = "#ffd700"          # Gold for Middle
COLOR_BAR_FOUND = "#28a745"        # Green
COLOR_BAR_DISCARDED = "#e0e0e0"    # Grey for discarded
COLOR_TEXT = "#000000"

class BinarySearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Binary Search Visualizer")
        self.root.geometry("900x600")
        self.root.configure(bg=COLOR_BG)

        self.data = []
        self.running = False
        self.target = None
        self.discarded_indices = set()

        self._setup_ui()
        self.generate_data()

    def _setup_ui(self):
        # Status
        self.status_var = tk.StringVar()
        self.status_var.set("Ready (Data must be sorted)")
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
        self.data = [random.randint(10, 100) for _ in range(15)]
        self.data.sort() # Critical for Binary Search
        self.discarded_indices = set()
        self.draw_bars(color_map={})
        self.status_var.set("New Sorted Array Generated")

    def draw_bars(self, color_map):
        self.canvas.delete("all")
        c_width = WIDTH
        c_height = HEIGHT
        
        x_width = c_width / len(self.data)
        offset = 10
        spacing = 5
        
        if not self.data: return
        max_val = max(self.data)
        normalized_data = [i / max_val for i in self.data]

        for i, height in enumerate(normalized_data):
            x0 = i * x_width + offset + spacing
            y0 = c_height - (height * (c_height - 50))
            x1 = (i + 1) * x_width + offset
            y1 = c_height

            val = self.data[i]
            
            # Determine Color
            if i in self.discarded_indices:
                color = COLOR_BAR_DISCARDED
            else:
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
        self.discarded_indices = set()
        threading.Thread(target=self.binary_search, daemon=True).start()

    def binary_search(self):
        low = 0
        high = len(self.data) - 1

        while low <= high:
            mid = (low + high) // 2
            mid_val = self.data[mid]
            
            # Visualize Range
            self.status_var.set(f"Checking range [{low}, {high}]. Mid index {mid} value is {mid_val}")
            
            # Color active range and mid
            color_map = {mid: COLOR_BAR_MID}
            for i in range(low, high + 1):
                if i != mid:
                    color_map[i] = COLOR_BAR_ACTIVE_RANGE
            
            self.update_ui(color_map)
            time.sleep(DELAY)

            if mid_val == self.target:
                self.status_var.set(f"Found {self.target} at index {mid}!")
                self.update_ui({mid: COLOR_BAR_FOUND})
                self.running = False
                return
            elif mid_val < self.target:
                self.status_var.set(f"{mid_val} < {self.target}. Discarding left half.")
                # Discard left half
                for i in range(low, mid + 1):
                    self.discarded_indices.add(i)
                low = mid + 1
            else:
                self.status_var.set(f"{mid_val} > {self.target}. Discarding right half.")
                # Discard right half
                for i in range(mid, high + 1):
                    self.discarded_indices.add(i)
                high = mid - 1
            
            self.update_ui({})
            time.sleep(DELAY)

        self.status_var.set(f"Value {self.target} not found.")
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
    app = BinarySearchApp(root)
    root.mainloop()
