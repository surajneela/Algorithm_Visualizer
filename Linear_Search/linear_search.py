"""Linear search visualizer using Tkinter.

This module provides a small GUI to demonstrate linear search
by animating checks over an array of integers.
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
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
    """Tkinter application that visualizes linear search.

    The app supports custom arrays, random generation, and an
    animated step-through of checking each element.
    """
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
        # self.generate_data() # Removed default generation
        self.root.after(100, self.prompt_startup_data) # Prompt immediately

    def prompt_startup_data(self):
        user_input = simpledialog.askstring("Input", "Enter numbers separated by commas (e.g., 5, 10, 2):", parent=self.root)
        if user_input:
            self.custom_entry.delete(0, tk.END)
            self.custom_entry.insert(0, user_input)
            self.use_custom_data()
        else:
            # If cancel, maybe generate random or just leave empty? User said "do not give me numbers".
            # Leaving empty.
            pass

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
        tk.Button(controls_frame, text="Generate Random", command=self.generate_data, **btn_style).pack(side=tk.LEFT, padx=10)

        # Custom Data Section
        custom_frame = tk.Frame(self.root, bg=COLOR_BG)
        custom_frame.pack(pady=10)
        tk.Label(custom_frame, te
                 xt="Custom Data (comma separated):", bg=COLOR_BG, font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=5)
        self.custom_entry = tk.Entry(custom_frame, font=("Segoe UI", 10), width=30)
        self.custom_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(custom_frame, text="Use Custom Data", command=self.use_custom_data, bg="#555", fg="white", relief="flat").pack(side=tk.LEFT, padx=5)

    def generate_data(self):
        if self.running: return
        self.data = [random.randint(10, 100) for _ in range(20)]
        self.draw_bars(color_map={})
        self.status_var.set("New Random Array Generated")

    def use_custom_data(self):
        if self.running: return
        raw_data = self.custom_entry.get()
        if not raw_data:
            messagebox.showwarning("Warning", "Please enter some numbers.")
            return
        
        try:
            # Parse CSV
            new_data = [int(x.strip()) for x in raw_data.split(',')]
            if not new_data: raise ValueError
            self.data = new_data
            self.draw_bars(color_map={})
            self.status_var.set("Custom Data Loaded")
        except ValueError:
            messagebox.showerror("Error", "Invalid format. Use comma-separated integers (e.g., 10, 20, 5).")

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
