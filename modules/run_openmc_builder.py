import tkinter as tk
from tkinter import filedialog, messagebox
import openmc
import os

import shutil  # For copying files

class RunOpenMCApp(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Run OpenMC Simulation")
        self.geometry("600x350")
        self.resizable(False, False)

        # Variables
        self.geometry_file = tk.StringVar()
        self.materials_file = tk.StringVar()
        self.settings_file = tk.StringVar()
        self.tallies_file = tk.StringVar()  # optional
        self.cross_file_var = tk.StringVar()

        # --- GUI ---
        self.add_browse_row("Geometry XML:", self.geometry_file)
        self.add_browse_row("Materials XML:", self.materials_file)
        self.add_browse_row("Settings XML:", self.settings_file)
        self.add_browse_row("Tallies XML (optional):", self.tallies_file)
        self.add_browse_row("Cross-Sections XML:", self.cross_file_var)

        tk.Button(self, text="Run OpenMC Simulation", command=self.run_openmc_sim, width=30, bg="lightgreen").pack(pady=10)
        tk.Button(self, text="Generate openmc_run.py", command=self.generate_openmc_run_file, width=30, bg="lightblue").pack()

        # ---------------- Developer credit label ----------------
        tk.Label(
            self,
            text="Developed by Mahmudul Hasan\n"
                "Nuclear Engineering, Dhaka University\n"
                "LinkedIn: linkedin.com/in/mhm-111",
            font=("Arial", 8),
            justify="right"
        ).place(relx=1, rely=0.98, anchor="se")


    def add_browse_row(self, label_text, var):
        tk.Label(self, text=label_text, anchor='w').pack(pady=(5,0), padx=10, fill='x')
        frame = tk.Frame(self)
        frame.pack(fill='x', padx=10, pady=2)
        tk.Entry(frame, textvariable=var, width=50).pack(side='left', padx=(0,5))
        tk.Button(frame, text="Browse", command=lambda v=var: self.browse_file(v)).pack(side='left')

    def browse_file(self, var):
        path = filedialog.askopenfilename(title="Select XML File", filetypes=[("XML Files", "*.xml")])
        if path:
            var.set(path)

    def run_openmc_sim(self):
        # Check mandatory files
        for f, name in [(self.geometry_file.get(),"geometry.xml"),
                        (self.materials_file.get(),"materials.xml"),
                        (self.settings_file.get(),"settings.xml"),
                        (self.cross_file_var.get(),"cross_sections.xml")]:
            if not f or not os.path.exists(f):
                messagebox.showerror("Error", f"Please select a valid {name}.")
                return

        # Optional tallies
        tallies_path = self.tallies_file.get()
        if tallies_path and not os.path.exists(tallies_path):
            messagebox.showerror("Error", "Tallies XML file does not exist.")
            return

        # Set cross_sections explicitly
        openmc.config['cross_sections'] = self.cross_file_var.get()

        # Run OpenMC in the directory of settings.xml (or any common folder)
        run_dir = os.path.dirname(self.settings_file.get())
        cwd = os.getcwd()
        os.chdir(run_dir)  # change working directory so OpenMC finds geometry.xml, materials.xml, settings.xml, tallies.xml
        try:
            messagebox.showinfo("Running", "Simulation started. This may take a while...")
            openmc.run()
            messagebox.showinfo("Success", f"OpenMC simulation completed!\nResults are stored in {run_dir}")
        except Exception as e:
            messagebox.showerror("Error", f"Simulation failed:\n{str(e)}")
        finally:
            os.chdir(cwd)  # go back to original directory


            # Optional tallies
            tallies_path = self.tallies_file.get()
            if tallies_path and not os.path.exists(tallies_path):
                messagebox.showerror("Error", "Tallies XML file does not exist.")
                return

        # Copy all files into output folder
        os.makedirs("output", exist_ok=True)
        shutil.copy(self.geometry_file.get(), "output/geometry.xml")
        shutil.copy(self.materials_file.get(), "output/materials.xml")
        shutil.copy(self.settings_file.get(), "output/settings.xml")
        shutil.copy(self.cross_file_var.get(), "output/cross_sections.xml")
        if tallies_path:
            shutil.copy(tallies_path, "output/tallies.xml")

        # Run OpenMC in output directory
        cwd = os.getcwd()
        os.chdir("output")
        try:
            messagebox.showinfo("Running", "Simulation started. This may take a while...")
            openmc.run()
            messagebox.showinfo("Success", "OpenMC simulation completed!\nResults are stored in 'output' directory.")
        except Exception as e:
            messagebox.showerror("Error", f"Simulation failed:\n{str(e)}")
        finally:
            os.chdir(cwd)

    def generate_openmc_run_file(self):
        # similar logic: copy files to output folder and generate run script
        pass
