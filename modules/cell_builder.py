import tkinter as tk
from tkinter import ttk, messagebox
import openmc
import os
import json

class CellBuilder:
    def __init__(self, master, surfaces, materials, universes):
        self.master = tk.Toplevel(master)
        self.master.title("Cell Builder")
        self.master.geometry("600x720")

        self.surfaces = surfaces
        self.universes = universes
        self.materials = self.load_materials()   # ✅ load materials.json here
        self.lattices = self.load_lattices()

        # Store cells in memory
        self.cells = []
        self.json_file = os.path.join("output", "cells.json")
        self.py_file = os.path.join("output", "geometry.py")

        self.load_cells_from_json()

        tk.Label(self.master, text="Create Cell", font=("Arial", 14)).pack(pady=6)

        tk.Label(self.master, text="Cell Name").pack()
        self.cell_name_entry = tk.Entry(self.master)
        self.cell_name_entry.pack(pady=3)

        tk.Label(self.master, text="Region Expression").pack()
        self.region_entry = tk.Entry(self.master, width=50)
        self.region_entry.pack(pady=3)
        tk.Label(
            self.master,
            text="Example: +s1 & -s2 | ~s3\n(use surface names you defined in Geometry Builder)",
            font=("Arial", 9),
            fg="gray"
        ).pack(pady=2)

        tk.Label(self.master, text="Available Surfaces:").pack()
        self.surface_listbox = tk.Listbox(self.master, width=60, height=6)
        self.surface_listbox.pack(pady=4)
        
        for name, info in self.surfaces.items():
            stype, sid, params = info["type"], info["id"], info["params"]
            btype = info.get("boundary_type", "")
            self.surface_listbox.insert(
                tk.END, f"{name} ({stype}), params={params}, boundary={btype}"
    )


        # Material dropdown
        tk.Label(self.master, text="Fill with Material").pack()
        mat_names = list(self.materials.keys()) if self.materials else []
        self.material_box = ttk.Combobox(self.master, values=mat_names, state="readonly")
        self.material_box.pack(pady=3)

        # Universe dropdown
        tk.Label(self.master, text="Fill with Universe (optional, overrides material)").pack()
        uni_names = list(self.universes.keys()) if self.universes else []
        self.universe_box = ttk.Combobox(self.master, values=uni_names, state="readonly")
        self.universe_box.pack(pady=3)

        # Lattice dropdown
        tk.Label(self.master, text="Fill with Lattice (optional, overrides universe & material)").pack()
        lat_names = list(self.lattices.keys()) if self.lattices else []
        self.lattice_box = ttk.Combobox(self.master, values=lat_names, state="readonly")
        self.lattice_box.pack(pady=3)

        # Buttons
        btn_frame = tk.Frame(self.master)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Add Cell", command=self.add_cell).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Save Cells", command=self.save_cells).grid(row=0, column=1, padx=5)

        # Cell list
        tk.Label(self.master, text="Created Cells:").pack()
        self.cell_listbox = tk.Listbox(self.master, width=70, height=8)
        self.cell_listbox.pack(pady=4)

        for cell in self.cells:
            self.cell_listbox.insert(
                tk.END,
                f"{cell['name']}: {cell['region']}, "
                f"material={cell.get('material','')}, "
                f"universe={cell.get('universe','')}, "
                f"lattice={cell.get('lattice','')}"
            )

    def load_cells_from_json(self):
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, "r") as f:
                    self.cells = json.load(f)
            except Exception as e:
                print(f"Error loading cells.json: {e}")
                self.cells = []

    def load_materials(self):
        """Load materials.json from output/"""
        materials_file = os.path.join("output", "materials.json")
        if os.path.exists(materials_file):
            try:
                with open(materials_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading materials.json: {e}")
        return {}

    def load_lattices(self):
        lattices_file = os.path.join("output", "lattices.json")
        if os.path.exists(lattices_file):
            try:
                with open(lattices_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading lattices.json: {e}")
        return {}

    def add_cell(self):
        name = self.cell_name_entry.get().strip()
        region = self.region_entry.get().strip()
        mat = self.material_box.get()
        uni = self.universe_box.get()
        lat = self.lattice_box.get()

        if not name or not region:
            messagebox.showerror("Error", "Missing inputs.")
            return
        if not mat and not uni and not lat:
            messagebox.showerror("Error", "Select a material, universe, or lattice to fill the cell.")
            return

        new_cell = {"name": name, "region": region}
        if lat:
            new_cell["lattice"] = lat
        elif uni:
            new_cell["universe"] = uni
        else:
            new_cell["material"] = mat

        self.cells.append(new_cell)
        self.cell_listbox.insert(
            tk.END,
            f"{name}: {region}, material={new_cell.get('material','')}, "
            f"universe={new_cell.get('universe','')}, lattice={new_cell.get('lattice','')}"
        )

    def save_cells(self):
        os.makedirs("output", exist_ok=True)

        # Save JSON
        with open(self.json_file, "w") as f:
            json.dump(self.cells, f, indent=2)

        # Save Python (geometry.py)
        lines = [
            "import openmc\n",
            "from surfaces import *\n",
            "from materials import *\n",
            "from geometry import universes\n",
            "from lattice import *\n\n",
        ]

        # Cells
        for cell in self.cells:
            if "lattice" in cell:
                fill = cell["lattice"]
            elif "universe" in cell:
                fill = f"universes['{cell['universe']}']"
            else:
                fill = cell["material"]
            lines.append(
                f"{cell['name']} = openmc.Cell(name='{cell['name']}', fill={fill}, region={cell['region']})\n"
            )

        # Create universes
        lines.append("\nuniverses = {}\n")
        for uni_name, uni_data in self.universes.items():
            uid = uni_data.get("id")
            cells_list = uni_data.get("cells", [])
            if uid:
                lines.append(
                    f"universes['{uni_name}'] = openmc.Universe(universe_id={uid}, name='{uni_name}')\n"
                )
            else:
                lines.append(f"universes['{uni_name}'] = openmc.Universe(name='{uni_name}')\n")
            for c in cells_list:
                lines.append(f"universes['{uni_name}'].add_cell({c})\n")

        # ⚠️ NOTE: We do not automatically build/export geometry here.
        # Geometry should be assembled in a separate driver script.
        lines.append(
            "\n# Example usage in run.py:\n"
            "# geometry = openmc.Geometry([cell1, cell2, ...])\n"
            "# geometry.export_to_xml('geometry.xml')\n"
        )

        with open(self.py_file, "w") as f:
            f.writelines(lines)

        messagebox.showinfo("Saved", f"Geometry saved to {self.py_file}")
