import tkinter as tk
from modules.material_builder import MaterialBuilder
from modules.geometry_builder import GeometryBuilder
from modules.universe_builder import UniverseBuilder
from modules.final_geometry_builder import open_final_geometry_window
from modules.lattice_builder import LatticeBuilder   # <-- import lattice builder
from modules.settings_builder import SettingsWindow
from modules.tallies_builder import TallyBuilderApp   # <-- import tallies builder
from modules.run_openmc_builder import RunOpenMCApp   # <-- import run OpenMC GUI


def main():
    root = tk.Tk()
    root.title("OpenMC GUI Builder")
    root.geometry("420x410")   # slightly increased height for extra button

    def open_material_builder():
        MaterialBuilder(root)

    def open_geometry_builder():
        GeometryBuilder(root)

    def open_final_geometry_builder():
        open_final_geometry_window()

    def open_universe_builder():
        import os, json

        # Load existing cells
        cells_path = os.path.join("output", "cells.json")
        if os.path.exists(cells_path):
            with open(cells_path, "r") as f:
                cells_data = json.load(f)
            cells = [c["name"] for c in cells_data]
        else:
            cells = []

        # Load existing materials
        materials_path = os.path.join("output", "materials.json")
        if os.path.exists(materials_path):
            with open(materials_path, "r") as f:
                materials_json = json.load(f)
            materials = {name: None for name in materials_json.keys()}
        else:
            materials = {}

        # Load existing universes
        universes_path = os.path.join("output", "universes.json")
        if os.path.exists(universes_path):
            with open(universes_path, "r") as f:
                universes = json.load(f)
        else:
            universes = {}

        UniverseBuilder(root, cells, materials, universes)

    def open_lattice_builder():
        LatticeBuilder(root)

    def open_settings_builder():
        SettingsWindow(root)

    def open_tallies_builder():
        TallyBuilderApp(root)   # <-- open tallies builder window

    def open_run_openmc():
        RunOpenMCApp(root)      # <-- Run OpenMC button callback

      
    tk.Label(root, text="OpenMC GUI Builder", font=("Arial", 20)).pack(pady=6)

    
    tk.Label(
        root,
        text="Developed by Mahmudul Hasan\n"
             "Nuclear Engineering, Dhaka University, Bangladesh\n"
             "Mail: mahmudul.du.ne8@gmail.com\n"
             "LinkedIn: linkedin.com/in/mhm-111\n"
             "---------------------------------",
        font=("Arial", 10),
        justify="center"
    ).pack(pady=3)

    


    # UI layout
    tk.Label(root, text="OpenMC GUI Builder Menu", font=("Arial", 16)).pack(pady=6)
    tk.Button(root, text="Create Material", command=open_material_builder, width=24).pack(pady=6)
    tk.Button(root, text="Create Geometry", command=open_geometry_builder, width=24).pack(pady=6)
    tk.Button(root, text="Create Universe", command=open_universe_builder, width=24).pack(pady=6)
    tk.Button(root, text="Create Lattice", command=open_lattice_builder, width=24).pack(pady=6)
    tk.Button(root, text="Create Final Geometry xml", command=open_final_geometry_builder, width=24).pack(pady=6)
    tk.Button(root, text="Simulation Settings", command=open_settings_builder, width=24).pack(pady=6)
    tk.Button(root, text="Tallies", command=open_tallies_builder, width=24).pack(pady=6)  
    tk.Button(root, text="Run OpenMC", command=open_run_openmc, width=24).pack(pady=6)  # <-- new button

    root.mainloop()


if __name__ == "__main__":
    main()
