import tkinter as tk
from tkinter import ttk, messagebox
import openmc
import os
import re
import json



# Common nuclides and elements
COMMON_NUCLIDES = ['Al27','B10','B11','Be9','Ca40','Ca42','Ca44','Cl35','Cl37','Cs137','Cu63','Cu65','F19','Fe54','Fe56','Fe57','Fe58','H1','H2','He3','He4','I131','K39','Kr85','Kr86','Li6','Li7','Mg24','Mg25','Mg26','Mo98','Mo100','Na23','Nb93','N14','N15','Ni58','Ni60','Ni62','O16','O17','O18','P31','Pu239','Pu240','Pu241','Pu242','S32','S33','S34','Si28','Si29','Si30','Sr90','Ta181','Th232','U233','U234','U235','U236','U238','W182','Xe135','Xe136','Zr90','Zr91','Zr92']
ELEMENTS = ['Al','B','Be','Ca','Cl','Cs','Cu','F','Fe','H','He','I','K','Kr','Li','Mg','Mo','Na','Nb','N','Ni','O','P','Pu','S','Si','Sr','Ta','Th','U','W','Xe','Zr']

THERMAL_SCATTERING = [
    "",  # blank means none
    "c_H_in_H2O",
    "c_H_in_CH2",
    "c_Graphite",
    "c_Be",
    "H_in_H2O",
    "D_in_D2O",
    "H_in_CH2",
    "H_in_ZrH",
    "Graphite",
    "Be_in_BeO"
]

BG_COLOR = "#8ad2e0"   # Ghost White
FG_COLOR = "#000000"   # Black text
ENTRY_BG = "#FFFFFF"   # Pure white for input fields
ENTRY_FG = "#000000"
BTN_BG = "#E0E0E0"     # Light gray button background
BTN_FG = "#000000"
HIGHLIGHT_BG = "#D3D3D3"  # Slightly darker gray for scrollbars




class MaterialBuilder(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Material Builder")
        self.geometry("600x700")
        self.resizable(True, True)

        # Scrollable frame
        canvas = tk.Canvas(self)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


        self.scrollable_frame.configure(bg=BG_COLOR)
        canvas.configure(bg=BG_COLOR)
        scrollbar.configure(bg=BG_COLOR, troughcolor=HIGHLIGHT_BG)


        # Variables
        self.available_nuclides = COMMON_NUCLIDES
        self.available_elements = ELEMENTS
        self.input_type_var = tk.StringVar(value="nuclide")
        self.material_name_var = tk.StringVar()
        self.density_var = tk.StringVar()
        self.temperature_var = tk.StringVar()
        self.nuclide_amount_var = tk.StringVar()
        self.enrichment_var = tk.StringVar()
        self.sab_var = tk.StringVar(value="")
        self.depletable_var = tk.BooleanVar(value=False)
        self.mix_var = tk.BooleanVar(value=False)
        self.nuclide_list = []

        self.build_gui()

    def build_gui(self):
        f = self.scrollable_frame

        tk.Label(
            self,
            text="Developed by Mahmudul Hasan\n"
                "Nuclear Engineering, Dhaka University\n"
                "LinkedIn: linkedin.com/in/mhm-111",
            font=("Helvetica", 8),
            justify="left"
        ).place(relx=.98, rely=0.98, anchor="se")

       

        tk.Label(f, text="Material Name:", bg=BG_COLOR, fg=FG_COLOR).pack(anchor='w', padx=80, pady=(5,0))
        tk.Entry(f, textvariable=self.material_name_var, bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=FG_COLOR).pack(fill='x', padx=80)
        tk.Label(f, text="Density (g/cm³):", bg=BG_COLOR, fg=FG_COLOR).pack(anchor='w', padx=80, pady=(5,0))
        tk.Entry(f, textvariable=self.density_var, bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=FG_COLOR).pack(fill='x', padx=80)
        tk.Label(f, text="Temperature (K) [optional]:", bg=BG_COLOR, fg=FG_COLOR).pack(anchor='w', padx=80, pady=(5,0))
        tk.Entry(f, textvariable=self.temperature_var, bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=FG_COLOR).pack(fill='x', padx=80)

        frame = tk.Frame(f)
        frame.pack(pady=5)
        tk.Label(frame, text="Add Type:", bg=BG_COLOR, fg=FG_COLOR).pack(side='left', padx=3)
        tk.Radiobutton(frame, text="Nuclide", variable=self.input_type_var, value="nuclide", command=self.update_dropdown).pack(side='left', padx=3)
        tk.Radiobutton(frame, text="Element", variable=self.input_type_var, value="element", command=self.update_dropdown).pack(side='left', padx=3)

        self.dropdown_label = tk.Label(f, text="Select Nuclide:", bg=BG_COLOR, fg=FG_COLOR)
        self.dropdown_label.pack(anchor='w', padx=80)
        self.nuclide_combo = ttk.Combobox(f, values=self.available_nuclides, state='readonly')
        self.nuclide_combo.pack(fill='x', padx=80)

        self.enrichment_label = tk.Label(f, text="Enrichment (%) [optional]:", bg=BG_COLOR, fg=FG_COLOR)
        self.enrichment_entry = tk.Entry(f, textvariable=self.enrichment_var)

        tk.Label(f, text="Atomic or Weight Fraction:", bg=BG_COLOR, fg=FG_COLOR).pack(anchor='w', padx=80, pady=(5,0))
        tk.Entry(f, textvariable=self.nuclide_amount_var, bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=FG_COLOR).pack(fill='x', padx=80)
        tk.Button(f, text="Add Nuclide/Element", command=self.add_nuclide, bg=BTN_BG, fg=BTN_FG, activebackground="#50fa7b").pack(pady=5)

        self.nuclide_listbox = tk.Listbox(f, height=10)
        self.nuclide_listbox.pack(fill='both', padx=80, pady=5, expand=True)

        tk.Label(f, text="Thermal Scattering (S(α,β)) [optional]:", bg=BG_COLOR, fg=FG_COLOR).pack(anchor='w', padx=80, pady=(5,0))
        ttk.Combobox(f, textvariable=self.sab_var, values=THERMAL_SCATTERING, state="readonly").pack(fill='x', padx=80)
        tk.Checkbutton(f, text="Depletable", variable=self.depletable_var).pack(anchor='w', padx=80, pady=3)

        # Mix materials
        tk.Checkbutton(f, text="Mix Previous Materials", variable=self.mix_var, command=self.toggle_mix_options).pack(anchor='w', padx=80, pady=3)
        self.prev_materials_listbox = tk.Listbox(f, selectmode='multiple', height=5)
        self.prev_materials_listbox.pack(fill='x', padx=80)
        self.prev_materials_listbox.config(state='disabled')

        tk.Label(f, text="Mixing Fractions (comma separated, sum=1)", bg=BG_COLOR, fg=FG_COLOR).pack(anchor='w', padx=80, pady=(2,0))
        self.mix_fractions_entry = tk.Entry(f, state='disabled')
        self.mix_fractions_entry.pack(fill='x', padx=80)

        tk.Button(f, text="Save Material to XML and Python", command=self.save_material, bg=BTN_BG, fg=BTN_FG, activebackground="#50fa7b").pack(pady=5)

        self.update_dropdown()

    def update_dropdown(self):
        if self.input_type_var.get() == "nuclide":
            self.nuclide_combo['values'] = self.available_nuclides
            self.nuclide_combo.set('')
            self.enrichment_label.pack_forget()
            self.enrichment_entry.pack_forget()
            self.dropdown_label.config(text="Select Nuclide:")
        else:
            self.nuclide_combo['values'] = self.available_elements
            self.nuclide_combo.set('')
            self.enrichment_label.pack(anchor='w', padx=80)
            self.enrichment_entry.pack(fill='x', padx=80)
            self.dropdown_label.config(text="Select Element:")

    def toggle_mix_options(self):
        if self.mix_var.get():
            self.prev_materials_listbox.config(state='normal')
            self.mix_fractions_entry.config(state='normal')
            # populate previous materials
            py_file = "output/materials.py"
            if os.path.exists(py_file):
                with open(py_file, "r") as f:
                    lines = f.readlines()
                materials = []
                for line in lines:
                    if line.startswith("# Material:"):
                        mat_name = line.split(":")[1].strip()
                        materials.append(mat_name)
                self.prev_materials_listbox.delete(0, tk.END)
                for m in materials:
                    self.prev_materials_listbox.insert(tk.END, m)
        else:
            self.prev_materials_listbox.config(state='disabled')
            self.mix_fractions_entry.config(state='disabled')

    def add_nuclide(self):
        name = self.nuclide_combo.get().strip()
        amount_str = self.nuclide_amount_var.get().strip()
        enrichment_str = self.enrichment_var.get().strip()
        input_type = self.input_type_var.get()

        if not name:
            messagebox.showwarning("Input Error", f"Please select a {input_type}.")
            return
        if not amount_str:
            messagebox.showwarning("Input Error", "Please enter the fraction amount.")
            return
        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showerror("Input Error", "Fraction amount must be a number.")
            return

        enrichment = None
        if input_type == "element" and enrichment_str:
            try:
                enrichment = float(enrichment_str)
                if enrichment < 0 or enrichment > 100:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Input Error", "Enrichment must be 0–100.")
                return

        entry = {'type': input_type, 'name': name, 'amount': amount, 'enrichment': enrichment}
        self.nuclide_list.append(entry)

        if input_type == "element":
            enrich_text = f", Enrichment: {enrichment}%" if enrichment is not None else ""
            display_text = f"Element: {name} - Fraction: {amount}{enrich_text}"
        else:
            display_text = f"Nuclide: {name} - Fraction: {amount}"

        self.nuclide_listbox.insert(tk.END, display_text)
        self.nuclide_combo.set('')
        self.nuclide_amount_var.set('')
        self.enrichment_var.set('')
    def save_material(self):
        name = self.material_name_var.get().strip()
        density_str = self.density_var.get().strip()
        temp_str = self.temperature_var.get().strip()

        # Check required fields
        if not name or not density_str:
            messagebox.showwarning("Input Error", "Material name and density are required.")
            return

        try:
            density = float(density_str)
        except ValueError:
            messagebox.showerror("Input Error", "Density must be a number.")
            return

        temperature = float(temp_str) if temp_str else None

        # Handle mix material
        is_mix = self.mix_var.get()
        mixed_materials = []
        fractions = []

        if is_mix:
            selected_indices = self.prev_materials_listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("Input Error", "Select at least one previous material to mix.")
                return

            # Get selected material names
            for idx in selected_indices:
                mixed_materials.append(self.prev_materials_listbox.get(idx))

            # Read fractions
            frac_str = self.mix_fractions_entry.get().strip()
            try:
                fractions = [float(f) for f in frac_str.split(",")]
            except:
                messagebox.showerror("Input Error", "Fractions must be numbers separated by commas.")
                return
            if len(fractions) != len(mixed_materials):
                messagebox.showerror("Input Error", "Number of fractions must match number of selected materials.")
                return
            if not abs(sum(fractions) - 1.0) < 1e-6:
                messagebox.showerror("Input Error", "Fractions must sum to 1.")
                return

        # Create OpenMC material
        mat = openmc.Material(name=name)
        mat.set_density('g/cm3', density)
        if temperature is not None:
            mat.temperature = temperature

        if not is_mix:
            # Normal material: add nuclides/elements
            for entry in self.nuclide_list:
                if entry['type'] == 'nuclide':
                    mat.add_nuclide(entry['name'], entry['amount'])
                else:
                    if entry['enrichment'] is not None:
                        mat.add_element(entry['name'], entry['amount'], enrichment=entry['enrichment'])
                    else:
                        mat.add_element(entry['name'], entry['amount'])

        # Thermal scattering
        if self.sab_var.get() and not is_mix:
            mat.add_s_alpha_beta(self.sab_var.get())

        # Depletable
        mat.depletable = self.depletable_var.get()

        # Save to XML
        os.makedirs("output", exist_ok=True)
        material_file = os.path.join("output", "materials.xml")
        mats = openmc.Materials.from_xml(material_file) if os.path.exists(material_file) else openmc.Materials()

        if is_mix:
            # Add fractions for mix materials using the previous Python materials
            #mat.add_nuclide("dummy", 0.0)  # placeholder to allow export
            # Custom attribute to store mix info
            mat.mix = {"materials": mixed_materials, "fractions": fractions}
        
        existing_ids = [m.id for m in mats]
        mat.id = max(existing_ids) + 1 if existing_ids else 1
        
        mats.append(mat)
        mats.export_to_xml(path=material_file)

        # -----------------------------
        # Generate Python code
        py_file = os.path.join("output", "materials.py")

        existing_code = ""
        material_names = []
        if os.path.exists(py_file):
            with open(py_file, 'r') as f:
                existing_code = f.read()
            material_names = re.findall(r'^(\w+)\s*=', existing_code, re.MULTILINE)

        lines = []
        lines.append(f"# Material: {name}")
        lines.append(f"{name} = openmc.Material(name='{name}')")
        lines.append(f"{name}.set_density('g/cm3', {density})")

        if not is_mix:
            for entry in self.nuclide_list:
                if entry['type'] == 'nuclide':
                    lines.append(f"{name}.add_nuclide('{entry['name']}', {entry['amount']})")
                else:
                    if entry['enrichment'] is not None:
                        lines.append(f"{name}.add_element('{entry['name']}', {entry['amount']}, enrichment={entry['enrichment']})")
                    else:
                        lines.append(f"{name}.add_element('{entry['name']}', {entry['amount']})")
            if self.sab_var.get():
                lines.append(f"{name}.add_s_alpha_beta('{self.sab_var.get()}')")
        else:
            # Mix material: store materials and fractions
            mix_list_str = ", ".join(mixed_materials)
            frac_list_str = ", ".join([str(f) for f in fractions])
            lines.append(f"# Mixed material: {name}")
            lines.append(f"{name}.mix = {{'materials': [{mix_list_str}], 'fractions': [{frac_list_str}]}}")

        lines.append(f"{name}.depletable = {self.depletable_var.get()}")

        material_names.append(name)

        with open(py_file, 'w') as f:
            f.write("import openmc\n\n")
            f.write("# Generated OpenMC materials file\n\n")
            if existing_code:
                prev_materials = re.split(r'materials_file\s*=\s*openmc\.Materials.*', existing_code)[0]
                f.write(prev_materials.strip() + "\n\n")
            f.write("\n".join(lines) + "\n\n")
            f.write(f"materials_file = openmc.Materials([{', '.join([m for m in material_names if m != 'materials_file'])}])\n")
            f.write("materials_file.export_to_xml('output/materials.xml')\n")


                # -----------------------------
        # Save also to JSON for CellBuilder
        json_file = os.path.join("output", "materials.json")
        try:
            if os.path.exists(json_file):
                with open(json_file, "r") as f:
                    materials_data = json.load(f)
            else:
                materials_data = {}
        except:
            materials_data = {}

        # Store basic info (no need to store full OpenMC object)
        materials_data[name] = {
            "density": density,
            "temperature": temperature,
            "depletable": self.depletable_var.get(),
            "is_mix": is_mix,
            "components": self.nuclide_list if not is_mix else None,
            "mix": {"materials": mixed_materials, "fractions": fractions} if is_mix else None
        }

        with open(json_file, "w") as f:
            json.dump(materials_data, f, indent=2)



        messagebox.showinfo("Success", f"Material '{name}' saved!\nFile: output/materials.xml\nPython code updated at output/materials.py")
        self.destroy()
