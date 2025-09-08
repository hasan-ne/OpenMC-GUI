import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class LatticeBuilder:
    def __init__(self, master):
        self.top = tk.Toplevel(master)
        self.top.title("Lattice Builder")
        self.top.geometry("500x600")
        self.top.resizable(False, False)

        self.universes = self.load_universes()
        self.ring_entries = []

        # ===== Lattice Properties =====
        tk.Label(self.top, text="Lattice Name:", font=("Arial", 11)).pack(pady=5)
        self.name_entry = tk.Entry(self.top, width=30)
        self.name_entry.pack(pady=5)

        tk.Label(self.top, text="Pitch (comma-separated):", font=("Arial", 11)).pack(pady=5)
        self.pitch_entry = tk.Entry(self.top, width=30)
        self.pitch_entry.insert(0, "1.275")
        self.pitch_entry.pack(pady=5)

        tk.Label(self.top, text="Orientation:", font=("Arial", 11)).pack(pady=5)
        self.orientation_dropdown = ttk.Combobox(self.top, values=["x", "y", "z"], state="readonly")
        self.orientation_dropdown.set("y")
        self.orientation_dropdown.pack(pady=5)

        tk.Label(self.top, text="Outer Universe:", font=("Arial", 11)).pack(pady=5)
        self.outer_dropdown = ttk.Combobox(self.top, values=self.universes, state="readonly")
        self.outer_dropdown.pack(pady=5)

        # ===== Rings Section =====
        tk.Label(self.top, text="Number of Rings:", font=("Arial", 11)).pack(pady=5)
        self.num_rings_spin = tk.Spinbox(self.top, from_=1, to=10, width=5, command=self.create_ring_inputs)
        self.num_rings_spin.pack(pady=5)

        self.rings_frame = tk.Frame(self.top)
        self.rings_frame.pack(pady=10, fill="x")

        # ===== Save Button =====
        save_btn = tk.Button(self.top, text="Save Lattice", command=self.save_lattice)
        save_btn.pack(pady=10)


        #credit
        tk.Label(
            self.top,
            text="Developed by Mahmudul Hasan\n"
                "Nuclear Engineering, Dhaka University\n"
                "LinkedIn: linkedin.com/in/mhm-111",
            font=("Helvetica", 8),
            justify="right"
        ).place(relx=0.98, rely=0.98, anchor="se")


        

    # -------- Load universes from JSON --------
    def load_universes(self):
        path = os.path.join("output", "universes.json")
        if not os.path.exists(path):
            return []

        try:
            with open(path, "r") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return list(data.keys())
            elif isinstance(data, list):
                return [u.get("name", f"Universe_{i}") for i, u in enumerate(data)]
            return []
        except Exception as e:
            print(f"Failed to load universes.json: {e}")
            return []

    # -------- Create ring dropdowns dynamically --------
    def create_ring_inputs(self):
        # Clear existing entries
        for widget in self.rings_frame.winfo_children():
            widget.destroy()
        self.ring_entries = []

        try:
            num_rings = int(self.num_rings_spin.get())
        except ValueError:
            num_rings = 1

        for i in range(num_rings, 0, -1):  # outer to inner
            tk.Label(self.rings_frame, text=f"Ring {i} universes (comma-separated names):", font=("Arial", 10)).pack(anchor="w", pady=2)
            entry = tk.Entry(self.rings_frame, width=50)
            entry.pack(pady=2)
            self.ring_entries.append(entry)

    # -------- Save lattice to lattice.py and lattices.json --------
    def save_lattice(self):
        name = self.name_entry.get().strip()
        pitch = self.pitch_entry.get().strip()
        orientation = self.orientation_dropdown.get().strip()
        outer = self.outer_dropdown.get().strip()

        if not name or not pitch or not orientation or not outer:
            messagebox.showerror("Error", "Please fill in all lattice fields.")
            return

        # Collect rings
        rings = []
        for entry in self.ring_entries:
            text = entry.get().strip()
            if not text:
                messagebox.showerror("Error", "Please fill in all ring fields.")
                return

            try:
                # Replace universe names with universes['name']
                safe_text = text
                for uni in self.universes:
                    safe_text = safe_text.replace(uni, f"universes['{uni}']")

                # Evaluate using eval with a safe environment where 'universes' is defined
                ring_obj = eval(safe_text, {"universes": {u: f"universes['{u}']" for u in self.universes}})
                rings.append(ring_obj)

            except Exception as e:
                messagebox.showerror("Error", f"Invalid ring format: {text}\n{e}")
                return

        # Ensure output folder exists
        os.makedirs("output", exist_ok=True)
        output_path = os.path.join("output", "lattice.py")

        # Generate Python code
        code_lines = [
            "import openmc\n",
            "from geometry import universes\n\n",
            f"{name} = openmc.HexLattice(name='{name}')\n",
            f"{name}.center = (0., 0.)\n",
            f"{name}.pitch = ({pitch},)\n",
            f"{name}.orientation = '{orientation}'\n",
            f"{name}.outer = universes['{outer}']\n\n",
            f"{name}.universes = [\n"
        ]
        for r in rings:
            code_lines.append(f"    {r},\n")
        code_lines.append("]\n")

        with open(output_path, "w") as f:
            f.writelines(code_lines)

        # ---- Update lattices.json ----
        lattices_json_path = os.path.join("output", "lattices.json")
        if os.path.exists(lattices_json_path):
            with open(lattices_json_path, "r") as f:
                try:
                    lattices = json.load(f)
                except Exception:
                    lattices = {}
        else:
            lattices = {}

        lattices[name] = {
            "name": name,
            "file": output_path
        }

        with open(lattices_json_path, "w") as f:
            json.dump(lattices, f, indent=4)

        messagebox.showinfo("Success", f"Lattice saved to {output_path} and recorded in lattices.json")
        self.top.destroy()
