import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import openmc

# Path for saved tallies
TALLY_JSON = "output/tallies.json"

# Predefined options
FILTER_OPTIONS = ["Cell", "Material", "Mesh", "Energy"]
SCORE_OPTIONS = ["flux", "fission", "nu-fission", "kappa-fission", "absorption", "scatter", "heating", "total"]
NUCLIDE_OPTIONS = ["U235", "U238", "H1", "O16"]  # Add more if needed

# --- Load previous tallies ---
def load_tallies():
    try:
        with open(TALLY_JSON, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# --- Save tallies to JSON ---
def save_tallies(data):
    os.makedirs("output", exist_ok=True)
    with open(TALLY_JSON, "w") as f:
        json.dump(data, f, indent=4)

# --- GUI App ---
class TallyBuilderApp:
    def __init__(self, master):
        # Create new popup window
        self.window = tk.Toplevel(master)
        self.window.title("OpenMC Tally Builder")
        self.window.geometry("750x450")

        # Previous tallies
        self.prev_tallies = load_tallies()

        # Left frame for tally input
        input_frame = ttk.Frame(self.window, padding=10)
        input_frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(input_frame, text="Tally Name:").grid(row=0, column=0, sticky="w")
        self.tally_name_entry = ttk.Entry(input_frame, width=30)
        self.tally_name_entry.grid(row=0, column=1, pady=5)

        ttk.Label(input_frame, text="Filter:").grid(row=1, column=0, sticky="w")
        self.filter_var = tk.StringVar()
        self.filter_dropdown = ttk.Combobox(
            input_frame, textvariable=self.filter_var,
            values=FILTER_OPTIONS, state="readonly"
        )
        self.filter_dropdown.grid(row=1, column=1, pady=5)

        ttk.Label(input_frame, text="Scores:").grid(row=2, column=0, sticky="w")
        self.scores_listbox = tk.Listbox(input_frame, selectmode="multiple", exportselection=0, height=6)
        for score in SCORE_OPTIONS:
            self.scores_listbox.insert(tk.END, score)
        self.scores_listbox.grid(row=2, column=1, pady=5)

        ttk.Label(input_frame, text="Nuclides:").grid(row=3, column=0, sticky="w")
        self.nuclides_listbox = tk.Listbox(input_frame, selectmode="multiple", exportselection=0, height=6)
        for nuc in NUCLIDE_OPTIONS:
            self.nuclides_listbox.insert(tk.END, nuc)
        self.nuclides_listbox.grid(row=3, column=1, pady=5)

        save_btn = ttk.Button(input_frame, text="Save Tally", command=self.save_tally)
        save_btn.grid(row=4, column=0, columnspan=2, pady=10)

        # Right frame for previous tallies
        right_frame = ttk.Frame(self.window, padding=10)
        right_frame.grid(row=0, column=1, sticky="nsew")

        ttk.Label(right_frame, text="Previous Tallies:").pack(anchor="w")
        self.tally_box = tk.Text(right_frame, width=50, height=25, state="disabled")
        self.tally_box.pack()
        self.refresh_tally_box()

        # ---------------- Developer credit label ----------------
        tk.Label(
            self.window,
            text="Developed by Mahmudul Hasan\n"
                "Nuclear Engineering, Dhaka University\n"
                "LinkedIn: linkedin.com/in/mhm-111",
            font=("Helvetica", 8),
            justify="right"
        ).place(relx=0.98, rely=0.98, anchor="se")


    # --- Refresh previous tallies ---
    def refresh_tally_box(self):
        self.tally_box.config(state="normal")
        self.tally_box.delete(1.0, tk.END)
        for t in self.prev_tallies:
            self.tally_box.insert(
                tk.END,
                f"Name: {t['name']}, Filter: {t['filter']}, Scores: {t['scores']}, Nuclides: {t['nuclides']}\n"
            )
        self.tally_box.config(state="disabled")

    # --- Save new tally ---
    def save_tally(self):
        name = self.tally_name_entry.get() or "unnamed_tally"
        filter_choice = self.filter_var.get()
        scores = [self.scores_listbox.get(i) for i in self.scores_listbox.curselection()]
        nuclides = [self.nuclides_listbox.get(i) for i in self.nuclides_listbox.curselection()]

        if not filter_choice or not scores:
            messagebox.showerror("Error", "Filter and at least one Score must be selected!")
            return

        new_tally = {"name": name, "filter": filter_choice, "scores": scores, "nuclides": nuclides}
        self.prev_tallies.append(new_tally)
        save_tallies(self.prev_tallies)

        self.export_openmc_tallies()
        self.refresh_tally_box()
        messagebox.showinfo("Saved", f"Tally '{name}' saved successfully!")

    # --- Export OpenMC Python + XML ---
    def export_openmc_tallies(self):
        tallies = openmc.Tallies()

        for t in self.prev_tallies:
            tally = openmc.Tally(name=t["name"])

            # Apply filter
            ftype = t.get("filter", "")
            if ftype == "Cell":
                tally.filters = [openmc.CellFilter([1])]  # placeholder
            elif ftype == "Material":
                tally.filters = [openmc.MaterialFilter([1])]
            elif ftype == "Mesh":
                mesh = openmc.RegularMesh()
                mesh.dimension = [5, 5, 1]
                mesh.lower_left = [0., 0., 0.]
                mesh.upper_right = [10., 10., 10.]
                tally.filters = [openmc.MeshFilter(mesh)]
            elif ftype == "Energy":
                tally.filters = [openmc.EnergyFilter([0.0, 0.625e-6, 20.0e6])]

            tally.scores = t.get("scores", [])
            if t.get("nuclides"):
                tally.nuclides = t["nuclides"]

            tallies.append(tally)

        # Export to XML
        os.makedirs("output", exist_ok=True)
        tallies.export_to_xml("output/tallies.xml")

        # Export to Python
        with open("output/tallies.py", "w") as f:
            f.write("import openmc\n\n")
            f.write("tallies = openmc.Tallies()\n\n")
            for i, t in enumerate(self.prev_tallies, start=1):
                f.write(f"# Tally {i}: {t['name']}\n")
                f.write(f"tally{i} = openmc.Tally(name='{t['name']}')\n")
                f.write(f"tally{i}.scores = {t['scores']}\n")
                if t['nuclides']:
                    f.write(f"tally{i}.nuclides = {t['nuclides']}\n")
                f.write(f"tallies.append(tally{i})\n\n")
            f.write("tallies.export_to_xml('output/tallies.xml')\n")
