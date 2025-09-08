import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import openmc
import numpy as np
import textwrap


class SettingsWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Simulation Settings")
        self.geometry("700x500")  # window height adjusted since tallies removed

        # ---------------- Notebook ----------------
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=8, pady=8)

        self.run_tab = ttk.Frame(notebook)
        self.source_tab = ttk.Frame(notebook)
        self.output_tab = ttk.Frame(notebook)

        notebook.add(self.run_tab, text="Run Settings")
        notebook.add(self.source_tab, text="Source Settings")
        notebook.add(self.output_tab, text="Output Options")

        # Build tabs
        self.build_run_tab()
        self.build_source_tab()
        self.build_output_tab()

        # ---------------- Bottom Buttons ----------------
        frame_bottom = tk.Frame(self)
        frame_bottom.pack(fill="x", side="bottom", pady=8)
        tk.Button(frame_bottom, text="Save Settings", command=self.save_settings).pack(side="left", padx=10)
        tk.Button(frame_bottom, text="Cancel", command=self.destroy).pack(side="right", padx=10)

        # ---------------- Developer credit label ----------------
        tk.Label(
            self,
            text="Developed by Mahmudul Hasan\n"
                "Nuclear Engineering, Dhaka University\n"
                "LinkedIn: linkedin.com/in/mhm-111",
            font=("Helvetica", 8),
            justify="right"
        ).place(relx=0.98, rely=0.85, anchor="se")


        

    # ---------------- Run Settings Tab ----------------
    def build_run_tab(self):
        f = self.run_tab
        tk.Label(f, text="Particles per batch:").grid(row=0, column=0, sticky="e", pady=4, padx=4)
        self.entry_particles = tk.Entry(f); self.entry_particles.insert(0, "1000"); self.entry_particles.grid(row=0, column=1, padx=4)
        tk.Label(f, text="Number of batches:").grid(row=1, column=0, sticky="e", pady=4, padx=4)
        self.entry_batches = tk.Entry(f); self.entry_batches.insert(0, "50"); self.entry_batches.grid(row=1, column=1, padx=4)
        tk.Label(f, text="Inactive batches:").grid(row=2, column=0, sticky="e", pady=4, padx=4)
        self.entry_inactive = tk.Entry(f); self.entry_inactive.insert(0, "10"); self.entry_inactive.grid(row=2, column=1, padx=4)
        tk.Label(f, text="Threads (blank=auto):").grid(row=3, column=0, sticky="e", pady=4, padx=4)
        self.entry_threads = tk.Entry(f); self.entry_threads.grid(row=3, column=1, padx=4)
        tk.Label(f, text="Random Seed (optional):").grid(row=4, column=0, sticky="e", pady=4, padx=4)
        self.entry_seed = tk.Entry(f); self.entry_seed.grid(row=4, column=1, padx=4)
        tk.Label(f, text="Run Mode:").grid(row=5, column=0, sticky="e", pady=4, padx=4)
        self.run_mode = ttk.Combobox(f, values=["Eigenvalue", "Fixed Source"], state="readonly")
        self.run_mode.set("Eigenvalue"); self.run_mode.grid(row=5, column=1, padx=4)
        tk.Label(f, text="Cross-section file:").grid(row=6, column=0, sticky="e", pady=4, padx=4)
        self.cross_file_var = tk.StringVar()
        tk.Entry(f, textvariable=self.cross_file_var, width=40).grid(row=6, column=1, padx=4)
        tk.Button(f, text="Browse", command=self.browse_cross_file).grid(row=6, column=2, padx=4)

    def browse_cross_file(self):
        path = filedialog.askopenfilename(title="Select Cross-Section XML File", filetypes=[("XML Files", "*.xml")])
        if path: self.cross_file_var.set(path)

    # ---------------- Source Tab ----------------
    def build_source_tab(self):
        f = self.source_tab
        tk.Label(f, text="Source Type:").grid(row=0, column=0, sticky="e", pady=4, padx=4)
        self.source_type = ttk.Combobox(f, values=["Point", "Box", "Spherical", "Cylindrical"], state="readonly")
        self.source_type.set("Point"); self.source_type.grid(row=0, column=1, padx=4)

        tk.Label(f, text="Position (x,y,z):").grid(row=1, column=0, sticky="e", pady=4, padx=4)
        self.entry_src_x = tk.Entry(f, width=8); self.entry_src_x.insert(0,"0"); self.entry_src_x.grid(row=1,column=1,sticky="w")
        self.entry_src_y = tk.Entry(f, width=8); self.entry_src_y.insert(0,"0"); self.entry_src_y.grid(row=1,column=1)
        self.entry_src_z = tk.Entry(f, width=8); self.entry_src_z.insert(0,"0"); self.entry_src_z.grid(row=1,column=1,sticky="e")

        tk.Label(f, text="Radius (if sphere/cylinder):").grid(row=2, column=0, sticky="e", pady=4, padx=4)
        self.entry_radius = tk.Entry(f); self.entry_radius.grid(row=2, column=1, padx=4)

        tk.Label(f, text="Box Extent (x_min,x_max,y_min,y_max,z_min,z_max):").grid(row=3,column=0,sticky="e",pady=4,padx=4)
        self.entry_extent = tk.Entry(f, width=40); self.entry_extent.grid(row=3,column=1,padx=4)

        tk.Label(f, text="Energy Distribution:").grid(row=4, column=0, sticky="e", pady=4, padx=4)

        # Add OpenMC Default for beginners
        self.energy_dist = ttk.Combobox(
            f, 
            values=["OpenMC Default", "Monoenergetic", "Watt Spectrum", "Maxwell Spectrum", "Tabular"], 
            state="readonly"
        )
        self.energy_dist.set("OpenMC Default")
        self.energy_dist.grid(row=4, column=1, padx=4)

        # Energy parameter entry (only relevant if not using default)
        self.energy_param = tk.Entry(f)
        self.energy_param.insert(0, "1e6")  # Keep 1 MeV default for Monoenergetic
        self.energy_param.grid(row=5, column=1, padx=4)

        tk.Button(f, text="Upload File (Tabular)", command=self.upload_energy_file).grid(row=5, column=2, padx=4)


    def upload_energy_file(self):
        path = filedialog.askopenfilename(title="Select Energy Spectrum File", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if path: self.energy_param.delete(0,tk.END); self.energy_param.insert(0,path)

    # ---------------- Output Tab ----------------
    def build_output_tab(self):
        f = self.output_tab
        self.var_statepoint = tk.BooleanVar(value=True)
        self.var_summary = tk.BooleanVar(value=True)
        self.var_restart = tk.BooleanVar(value=False)
        tk.Checkbutton(f, text="statepoint.h5", variable=self.var_statepoint).pack(anchor="w", padx=10, pady=4)
        tk.Checkbutton(f, text="summary.h5", variable=self.var_summary).pack(anchor="w", padx=10, pady=4)
        tk.Checkbutton(f, text="restart.h5", variable=self.var_restart).pack(anchor="w", padx=10, pady=4)
        #tk.Label(f, text="Verbosity:").pack(anchor="w", padx=10, pady=4)
        #self.verbosity = ttk.Combobox(f, values=["1","2","3"], state="readonly"); self.verbosity.set("2"); self.verbosity.pack(anchor="w", padx=10, pady=4)

    # ---------------- Save Settings ----------------
    def save_settings(self):
        import os, json, textwrap, numpy as np
        import openmc

        os.makedirs("output", exist_ok=True)

        # --- Collect JSON dictionary ---
        settings_dict = {
            "particles": int(self.entry_particles.get()),
            "batches": int(self.entry_batches.get()),
            "inactive": int(self.entry_inactive.get() or 0),
            "threads": self.entry_threads.get() or None,
            "seed": self.entry_seed.get() or None,
            "run_mode": self.run_mode.get(),
            "cross_sections": self.cross_file_var.get() or os.environ.get("OPENMC_CROSS_SECTIONS", None),
            "source": {
                "type": self.source_type.get(),
                "position": [float(self.entry_src_x.get()), float(self.entry_src_y.get()), float(self.entry_src_z.get())],
                "radius": float(self.entry_radius.get()) if self.entry_radius.get() else None,
                "extent": [float(x) for x in self.entry_extent.get().split(",")] if self.entry_extent.get() else None,
                "energy": {"dist": self.energy_dist.get(), "param": self.energy_param.get()}
            },
            
            "outputs": {
                "statepoint": self.var_statepoint.get(),
                "summary": self.var_summary.get(),
                
                "restart": self.var_restart.get()
                #"verbosity": int(self.verbosity.get())
            }
        }

        # --- Save Python settings file ---
        with open("output/settings.py", "w") as f:
            f.write(textwrap.dedent(f"""\
        import openmc
        import numpy as np

        # ---------------- User-editable settings ----------------
        settings = {settings_dict}

        # ---------------- Build OpenMC Settings ----------------
        s = openmc.Settings()
        s.run_mode = settings['run_mode'].lower().replace(" ", "_")
        s.particles = settings['particles']
        s.batches = settings['batches']
        s.inactive = settings['inactive']
        s.threads = settings['threads']
        if settings['seed'] is not None:
            s.seed = settings['seed']
        s.cross_sections = settings['cross_sections']

        # ---------------- Source ----------------
        src_data = settings['source']
        src = openmc.Source()
        pos = src_data['position']
        radius = src_data['radius']
        extent = src_data['extent']

        # Space object for IndependentSource
        if src_data['type'] == "Point":
            src.space = openmc.stats.Point(pos)
        elif src_data['type'] == "Spherical":
            # approximate sphere with box
            src.space = openmc.stats.Box(
                lower_left=[pos[0]-radius, pos[1]-radius, pos[2]-radius],
                upper_right=[pos[0]+radius, pos[1]+radius, pos[2]+radius]
            )
        elif src_data['type'] == "Cylindrical":
            # approximate cylinder with box (height=2)
            src.space = openmc.stats.Box(
                lower_left=[pos[0]-radius, pos[1]-radius, pos[2]-1],
                upper_right=[pos[0]+radius, pos[1]+radius, pos[2]+1]
            )
        elif src_data['type'] == "Box":
            if extent and len(extent) == 6:
                src.space = openmc.stats.Box(
                    lower_left=[extent[0], extent[2], extent[4]],
                    upper_right=[extent[1], extent[3], extent[5]]
                )
            else:
                src.space = openmc.stats.Box(
                    lower_left=[pos[0]-1, pos[1]-1, pos[2]-1],
                    upper_right=[pos[0]+1, pos[1]+1, pos[2]+1]
                )

                

        # ---------------- Energy ----------------
        energy = src_data['energy']
        dist = energy['dist']
        param = energy['param']

        if dist == 'Monoenergetic':
            src.energy = openmc.stats.Discrete([float(param)], [1.0])
        elif dist == 'Watt Spectrum':
            a, b = [float(x) for x in param.split(",")]
            src.energy = openmc.stats.Watt(a, b)
        elif dist == 'Maxwell Spectrum':
            src.energy = openmc.stats.Maxwell(float(param))
        elif dist == 'Tabular':
            data = np.loadtxt(param)
            src.energy = openmc.stats.Discrete(data[:,0].tolist(), data[:,1].tolist())

        s.source = src

        # ---------------- Tallies ----------------
        # Example: user can later add tally definitions here using settings['tallies']
        # for t in settings['tallies']:
        #     tally = openmc.Tally(name=t['type'])
        #     s.tallies.append(tally)

        # ---------------- Output options ----------------
        # Example: verbosity and outputs can be customized here
        # s.verbosity = settings['outputs']['verbosity']

        # ---------------- Export ----------------
        s.export_to_xml("output/settings.xml")
        print("settings.xml generated successfully")

        """))


        # --- Create OpenMC Settings object ---
        s = openmc.Settings()
        s.run_mode = self.run_mode.get().lower().replace(" ", "_")
        s.particles = int(self.entry_particles.get())
        s.batches = int(self.entry_batches.get())
        s.inactive = int(self.entry_inactive.get() or 0)
        s.threads = int(self.entry_threads.get()) if self.entry_threads.get() else None
        if self.entry_seed.get():
            s.seed = int(self.entry_seed.get())
        s.cross_sections = self.cross_file_var.get() or os.environ.get("OPENMC_CROSS_SECTIONS", None)
        #s.verbosity = int(self.verbosity.get())

        # --- Configure Source ---
        src_type = self.source_type.get()
        pos = [float(self.entry_src_x.get()), float(self.entry_src_y.get()), float(self.entry_src_z.get())]
        radius = float(self.entry_radius.get()) if self.entry_radius.get() else 1.0
        extent = [float(x) for x in self.entry_extent.get().split(",")] if self.entry_extent.get() else None

        # Space object for IndependentSource
        if src_type == "Point":
            space = openmc.stats.Point(pos)
        elif src_type == "Spherical":
            # approximate sphere with box
            space = openmc.stats.Box(
                lower_left=[pos[0]-radius, pos[1]-radius, pos[2]-radius],
                upper_right=[pos[0]+radius, pos[1]+radius, pos[2]+radius]
            )
        elif src_type == "Cylindrical":
            # approximate cylinder with box (height=2)
            space = openmc.stats.Box(
                lower_left=[pos[0]-radius, pos[1]-radius, pos[2]-1],
                upper_right=[pos[0]+radius, pos[1]+radius, pos[2]+1]
            )
        elif src_type == "Box":
            if extent and len(extent) == 6:
                space = openmc.stats.Box(
                    lower_left=[extent[0], extent[2], extent[4]],
                    upper_right=[extent[1], extent[3], extent[5]]
                )
            else:
                space = openmc.stats.Box(
                    lower_left=[pos[0]-1, pos[1]-1, pos[2]-1],
                    upper_right=[pos[0]+1, pos[1]+1, pos[2]+1]
                )

        # Energy object
    
        # ---------------- Energy ----------------
        energy_dist = self.energy_dist.get()
        param = self.energy_param.get()

        try:
            if energy_dist == "OpenMC Default":
                # OpenMC default: do not pass energy
                src = openmc.source.IndependentSource(space=space)
            elif energy_dist == "Monoenergetic":
                energy = openmc.stats.Discrete([float(param)], [1.0])
                src = openmc.source.IndependentSource(space=space, energy=energy)
            elif energy_dist == "Watt Spectrum":
                a, b = [float(x) for x in param.split(",")]
                energy = openmc.stats.Watt(a, b)
                src = openmc.source.IndependentSource(space=space, energy=energy)
            elif energy_dist == "Maxwell Spectrum":
                energy = openmc.stats.Maxwell(float(param))
                src = openmc.source.IndependentSource(space=space, energy=energy)
            elif energy_dist == "Tabular":
                data = np.loadtxt(param)
                energy = openmc.stats.Discrete(data[:, 0].tolist(), data[:, 1].tolist())
                src = openmc.source.IndependentSource(space=space, energy=energy)
        except Exception as e:
            messagebox.showerror("Error", f"Invalid energy parameters: {param}\n{e}")
            return

        # Assign to settings


        s.source = src

        # --- Export settings.xml ---
        s.export_to_xml("output/settings.xml")

    

        messagebox.showinfo("Saved", "Settings saved to Python and XML files in output folder")
