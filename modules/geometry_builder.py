import tkinter as tk
from tkinter import ttk, messagebox
import os
import openmc
import json
from .cell_builder import CellBuilder
from .utils import load_materials_from_xml


class GeometryBuilder:
    def __init__(self, master):
        self.master = tk.Toplevel(master)
        self.master.title("Geometry Builder")
        self.master.geometry("500x550")  # slightly taller to fit new dropdown

        self.surfaces = self.load_surfaces_from_json()
        self.surface_listbox = None

        # Materials for cell builder
        self.materials_by_name = load_materials_from_xml()


        

        tk.Label(self.master, text="Create Surfaces", font=("Arial", 14)).pack(pady=6)

        # Surface name
        tk.Label(self.master, text="Surface Name").pack()
        self.surface_name_entry = tk.Entry(self.master)
        self.surface_name_entry.pack(pady=3)

        # Surface ID
        tk.Label(self.master, text="Surface ID (optional)").pack()
        self.surface_id_entry = tk.Entry(self.master)
        self.surface_id_entry.pack(pady=3)

        # Surface type dropdown
        tk.Label(self.master, text="Surface Type").pack()
        self.surface_type = ttk.Combobox(
            self.master,
            values=["XPlane", "YPlane", "ZPlane", "ZCylinder", "HexagonalPrism"]
        )
        self.surface_type.pack(pady=3)
        self.surface_type.bind("<<ComboboxSelected>>", self.update_parameter_fields)

        # Boundary type dropdown (optional)
        tk.Label(self.master, text="Boundary Type (optional)").pack()
        self.boundary_type = ttk.Combobox(
            self.master,
            values=["", "transmission", "vacuum", "reflective", "periodic", "white"],
            state="readonly"
        )
        self.boundary_type.current(0)  # default empty (no boundary)
        self.boundary_type.pack(pady=3)

        # Dynamic parameter frame
        self.param_frame = tk.Frame(self.master)
        self.param_frame.pack(pady=6)

        # Add surface button
        tk.Button(self.master, text="Add Surface", command=self.add_surface).pack(pady=6)

        # Surface list
        tk.Label(self.master, text="Created Surfaces:").pack()
        self.surface_listbox = tk.Listbox(self.master, width=60, height=8)
        self.surface_listbox.pack(pady=4)
        self.refresh_surface_listbox()

        # Save surfaces button
        tk.Button(self.master, text="Save Surfaces", command=self.save_surfaces).pack(pady=10)

        # Open Cell Builder
        tk.Button(self.master, text="Open Cell Builder", command=self.open_cell_builder).pack(pady=6)

        # Developer credit label (top-right corner)
        tk.Label(
            self.master,
            text="Developed by Mahmudul Hasan\n"
                "Nuclear Engineering, Dhaka University\n"
                "LinkedIn: linkedin.com/in/mhm-111",
            font=("Helvetica", 8),
            justify="left"
        ).place(relx=0.98, rely=0.98, anchor="se")


    def update_parameter_fields(self, event=None):
        """Show parameter fields depending on surface type"""
        for widget in self.param_frame.winfo_children():
            widget.destroy()

        surface_type = self.surface_type.get()

        if surface_type == "XPlane":
            tk.Label(self.param_frame, text="x0:").grid(row=0, column=0)
            self.param_entry = tk.Entry(self.param_frame)
            self.param_entry.grid(row=0, column=1)

        elif surface_type == "YPlane":
            tk.Label(self.param_frame, text="y0:").grid(row=0, column=0)
            self.param_entry = tk.Entry(self.param_frame)
            self.param_entry.grid(row=0, column=1)

        elif surface_type == "ZPlane":
            tk.Label(self.param_frame, text="z0:").grid(row=0, column=0)
            self.param_entry = tk.Entry(self.param_frame)
            self.param_entry.grid(row=0, column=1)

        elif surface_type == "ZCylinder":
            tk.Label(self.param_frame, text="Radius:").grid(row=0, column=0)
            self.param_entry = tk.Entry(self.param_frame)
            self.param_entry.grid(row=0, column=1)

        elif surface_type == "HexagonalPrism":
            tk.Label(self.param_frame, text="Edge Length:").grid(row=0, column=0)
            self.edge_entry = tk.Entry(self.param_frame)
            self.edge_entry.grid(row=0, column=1)

            tk.Label(self.param_frame, text="Orientation (x/y/z):").grid(row=1, column=0)
            self.orientation_entry = tk.Entry(self.param_frame)
            self.orientation_entry.grid(row=1, column=1)

    def add_surface(self):
        """Add surface and show in list"""
        name = self.surface_name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Surface must have a name.")
            return

        surface_type = self.surface_type.get()
        sid = self.surface_id_entry.get().strip()
        sid = int(sid) if sid else None

        # boundary type
        btype = self.boundary_type.get().strip()
        btype = btype if btype else None

        if surface_type in ["XPlane", "YPlane", "ZPlane", "ZCylinder"]:
            param = self.param_entry.get().strip()
            if not param:
                messagebox.showerror("Error", "Missing parameter value.")
                return
            params = [param]
        elif surface_type == "HexagonalPrism":
            edge = self.edge_entry.get().strip()
            ori = self.orientation_entry.get().strip()
            if not edge or not ori:
                messagebox.showerror("Error", "Missing hexagon parameters.")
                return
            params = [edge, ori]
        else:
            return

        self.surfaces[name] = {
            "type": surface_type,
            "id": sid,
            "params": params,
            "boundary_type": btype  # ✅ save boundary type
        }
        self.refresh_surface_listbox()
        self.save_surfaces_json()

    def refresh_surface_listbox(self):
        self.surface_listbox.delete(0, tk.END)
        for name, info in self.surfaces.items():
            btxt = f", boundary={info['boundary_type']}" if info.get("boundary_type") else ""
            self.surface_listbox.insert(
                tk.END, f"{name} ({info['type']}) params={info['params']}{btxt}"
            )

    def save_surfaces_json(self):
        out_dir = "output"
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "surfaces.json"), "w") as f:
            json.dump(self.surfaces, f, indent=2)

    def load_surfaces_from_json(self):
        path = os.path.join("output", "surfaces.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return {}

    def save_surfaces(self):
        """Save surfaces to Python file"""
        py_file = "output/surfaces.py"

        lines = ["import openmc\n\n"]

        for name, info in self.surfaces.items():
            stype, sid, params, btype = info["type"], info["id"], info["params"], info.get("boundary_type")
            boundary_kw = f", boundary_type='{btype}'" if btype else ""

            if stype == "XPlane":
                code = f"{name} = openmc.XPlane(surface_id={sid}, x0={params[0]}{boundary_kw})\n" if sid else f"{name} = openmc.XPlane(x0={params[0]}{boundary_kw})\n"
            elif stype == "YPlane":
                code = f"{name} = openmc.YPlane(surface_id={sid}, y0={params[0]}{boundary_kw})\n" if sid else f"{name} = openmc.YPlane(y0={params[0]}{boundary_kw})\n"
            elif stype == "ZPlane":
                code = f"{name} = openmc.ZPlane(surface_id={sid}, z0={params[0]}{boundary_kw})\n" if sid else f"{name} = openmc.ZPlane(z0={params[0]}{boundary_kw})\n"
            elif stype == "ZCylinder":
                code = f"{name} = openmc.ZCylinder(surface_id={sid}, r={params[0]}{boundary_kw})\n" if sid else f"{name} = openmc.ZCylinder(r={params[0]}{boundary_kw})\n"
            elif stype == "HexagonalPrism":
                code = f"{name} = openmc.model.HexagonalPrism(edge_length={params[0]}, orientation='{params[1]}'{boundary_kw})\n"
            lines.append(code)

        with open(py_file, "w") as f:
            f.writelines(lines)
            f.write("\n# Surfaces are used in regions, no direct XML export.\n")

        messagebox.showinfo("Saved", f"Surfaces saved to {py_file}")

    def open_cell_builder(self):
        # Load universes from JSON
        universes_path = os.path.join("output", "universes.json")
        if os.path.exists(universes_path):
            with open(universes_path, "r") as f:
                universes = json.load(f)
        else:
            universes = {}  # empty if no universes exist yet

        # Open CellBuilder with surfaces, materials, and universes
        CellBuilder(self.master, self.surfaces, self.materials_by_name, universes)
