import tkinter as tk
from tkinter import messagebox
import os
import json
import openmc

class UniverseBuilder:
    def __init__(self, master, cells, materials, universes):
        self.master = tk.Toplevel(master)
        self.master.title("Universe Builder")
        self.master.geometry("600x550")

        # Files
        self.json_file = os.path.join("output", "universes.json")
        self.py_file = os.path.join("output", "geometry.py")

        # Load predefined cells
        self.cells = cells  # list of cell names
        self.materials = materials
        self.universes = universes  # existing universes from JSON

        # ---- GUI ----
        tk.Label(self.master, text="Create Universe", font=("Arial", 14)).pack(pady=8)

        # Universe name
        tk.Label(self.master, text="Universe Name:").pack()
        self.name_entry = tk.Entry(self.master)
        self.name_entry.pack(pady=4)

        # Universe ID
        tk.Label(self.master, text="Universe ID (optional):").pack()
        self.id_entry = tk.Entry(self.master)
        self.id_entry.pack(pady=4)

        # Predefined cells selection
        tk.Label(self.master, text="Select Predefined Cells:").pack()
        self.cells_listbox = tk.Listbox(self.master, selectmode=tk.MULTIPLE, height=8)
        self.cells_listbox.pack(pady=6, fill=tk.X, padx=20)
        for cell_name in self.cells:
            self.cells_listbox.insert(tk.END, cell_name)

        # Buttons
        btn_frame = tk.Frame(self.master)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Add Universe", command=self.add_universe).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Save Universes", command=self.save_universes).grid(row=0, column=1, padx=5)

        # Created universes
        tk.Label(self.master, text="Created Universes:").pack()
        self.universe_listbox = tk.Listbox(self.master, width=70, height=8)
        self.universe_listbox.pack(pady=6)
        self.refresh_universe_listbox()

        tk.Label(
            self.master,
            text="Developed by Mahmudul Hasan\n"
                "Nuclear Engineering, Dhaka University\n"
                "LinkedIn: linkedin.com/in/mhm-111",
            font=("Helvetica", 8),
            justify="left"
        ).place(relx=0.98, rely=0.98, anchor="se")

    # ---- Functions ----
    def refresh_universe_listbox(self):
        self.universe_listbox.delete(0, tk.END)
        for name, data in self.universes.items():
            uid = data.get("id", "")
            cells = ", ".join(data.get("cells", []))
            self.universe_listbox.insert(tk.END, f"{name} (ID={uid}): {cells}")

    def add_universe(self):
        name = self.name_entry.get().strip()
        uid = self.id_entry.get().strip()
        uid = int(uid) if uid else None
        selected_indices = self.cells_listbox.curselection()
        selected_cells = [self.cells_listbox.get(i) for i in selected_indices]

        if not name:
            messagebox.showerror("Error", "Universe name cannot be empty.")
            return
        if name in self.universes:
            messagebox.showwarning("Warning", f"Universe '{name}' already exists.")
            return

        self.universes[name] = {"id": uid, "cells": selected_cells}
        self.refresh_universe_listbox()

    def save_universes(self):
        os.makedirs("output", exist_ok=True)

        # Save JSON
        with open(self.json_file, "w") as f:
            json.dump(self.universes, f, indent=2)

        # Save Python (geometry.py)
        lines = ["import openmc\nfrom surfaces import *\nfrom materials import *\n\n"]

        # Cells first
        cells_json_path = os.path.join("output", "cells.json")
        if os.path.exists(cells_json_path):
            with open(cells_json_path, "r") as f:
                cells_data = json.load(f)
            for cell in cells_data:
                fill = cell.get("material") or cell.get("universe")
                lines.append(f"{cell['name']} = openmc.Cell(name='{cell['name']}', fill={fill}, region={cell['region']})\n")

        # Universes
        lines.append("\nuniverses = {}\n")
        for uni_name, uni_data in self.universes.items():
            uid = uni_data.get("id")
            cells_list = uni_data.get("cells", [])
            if uid:
                lines.append(f"universes['{uni_name}'] = openmc.Universe(universe_id={uid}, name='{uni_name}')\n")
            else:
                lines.append(f"universes['{uni_name}'] = openmc.Universe(name='{uni_name}')\n")
            for c in cells_list:
                lines.append(f"universes['{uni_name}'].add_cell({c})\n")

        # Geometry
        cell_names = ", ".join([c["name"] for c in cells_data])
        if cell_names:
            lines.append(f"\ngeometry = openmc.Geometry([{cell_names}])\n")
            #lines.append("geometry.export_to_xml('output/geometry.xml')\n")

        with open(self.py_file, "w") as f:
            f.writelines(lines)

        messagebox.showinfo("Saved", f"Geometry saved to {self.py_file}")
