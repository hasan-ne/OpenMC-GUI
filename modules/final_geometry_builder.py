import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import openmc

def load_universes():
    """Load universe names from output/universes.json"""
    path = os.path.join("output", "universes.json")
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        try:
            universes = json.load(f)
            return list(universes.keys())
        except Exception as e:
            print("Error loading universes.json:", e)
            return []

def save_final_geometry(selected_universe):
    """Generate final_geometry.py using the selected universe"""
    if not selected_universe:
        messagebox.showerror("Error", "Please select a universe.")
        return

    # Ensure output folder exists
    os.makedirs("output", exist_ok=True)
    output_path = os.path.join("output", "final_geometry.py")

    # Generate Python code
    code_lines = [
        "import openmc\nfrom geometry import *  # import all previously defined universes/cells\n",
        "\n",
        f"geometry = openmc.Geometry(universes['{selected_universe}'])\n",
         "geometry.export_to_xml('output/geometry.xml')\n",
         f"print('Final geometry created with universe: {selected_universe}')\n"
    ]

    # Save file in output folder
    with open(output_path, "w") as f:
        f.writelines(code_lines)

    # Show confirmation and close window
    messagebox.showinfo(
        "Success",
        f"final_geometry.py created in output folder with universe: {selected_universe}"
    )

def open_final_geometry_window():
    """Open GUI window for selecting universe and saving final_geometry.py"""
    root = tk.Tk()
    root.title("Final Geometry Builder")
    root.geometry("350x180")

    universe_list = load_universes()

    tk.Label(root, text="Select a Universe:", font=("Arial", 12)).pack(pady=10)

    dropdown = ttk.Combobox(root, values=universe_list, state="readonly")
    dropdown.pack(pady=5)

    tk.Label(
            root,
            text="Developed by Mahmudul Hasan\n"
                "Nuclear Engineering, Dhaka University\n"
                "LinkedIn: linkedin.com/in/mhm-111",
            font=("Helvetica", 8),
            justify="left"
        ).place(relx=.98, rely=0.98, anchor="se")

    def on_save():
        selected_universe = dropdown.get().strip()  # get directly from Combobox
        if not selected_universe:
            messagebox.showerror("Error", "Please select a universe.")
            return

        # Save final_geometry.py
        save_final_geometry(selected_universe)
        root.destroy()  # close the window

    save_button = tk.Button(root, text="Save Final Geometry", command=on_save)
    save_button.pack(pady=20)

    root.mainloop()


if __name__ == "__main__":
    open_final_geometry_window()
