# 🚀 OpenMC GUI Builder

[![Python](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/) 
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE) 
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Mahmudul_Hasan-blue)](https://www.linkedin.com/in/your-linkedin)

**Developed by Mahmudul Hasan**  
Nuclear Engineering, Dhaka University, Bangladesh  
📧 mahmudul.du.ne8@gmail.com  

---

## 💡 Overview

**OpenMC GUI Builder** is a **user-friendly graphical interface** for creating, managing, and running OpenMC simulations. It eliminates the need to manually write XML files, making OpenMC accessible to students, researchers, and engineers.

With this GUI, you can define:

- Materials  
- Geometries and Cells  
- Universes & Lattices  
- Source and Energy Distributions  
- Tallies  
- Simulation settings  
and run simulations directly from the interface.

---

## ✨ Features

#### 1.Material Builder
- Create  materials with atomic densities and isotopic compositions.
- Can export xml file directly for openmc.
- Also can generate a python file named **materials.py**. Using this user can easily change the parameters in future if he wants.

#### 2.Geometry Builder
- Define cells, surfaces, and spatial relationships.  

#### 3.Universe Builder
- Combine cells into universes for complex reactor models.  

#### 4.Lattice Builder
- Build structured or repeating lattice geometries effortlessly.  

#### 5.Final Geometry Export
- Export **geometry.xml** ready for OpenMC.
- Will also export a python file for future use for the user.

#### 6.Simulation Settings
- Configure particles, batches, source distributions, and energy spectra.  

#### 7.Tallies Builder
- Add tally definitions for neutron flux, reaction rates, and more.  

#### 8.Run OpenMC
- Execute simulations **directly from the GUI**.  

#### 9.Energy Spectrum Support
- Monoenergetic, Watt, Maxwell, Tabular, or OpenMC default spectrum.

#### 10.XML and Python file
- This tool can generate xml files for materials, geometry, settings and tallies. Which an user can use directly to run openmc.
- It also generates python files. (eg: materils.py, geometry.py, settings.py etc ). Using these python files user can change the parameters in the code and export xml files in future for further analysis.

---

## 🛠 Installation

```bash
# Clone the repository
git clone https://github.com/hasan-ne/OpenMC-GUI.git
cd OpenMC-GUI

# Create a Python environment
conda create -n openmc-env python=3.12
conda activate openmc-env

# Install dependencies
conda install -c conda-forge openmc numpy pandas pillow tqdm

# Run Tool
python3 main.py

```
---
### Requirements:
  - openmc
  - numpy
  - tkinter (usually comes with Python)
  - Ensure OpenMC is installed and configured: [OpenMC Installation Guide](https://docs.openmc.org/en/stable/quickinstall.html)

-----
### Installation Video
[▶ Watch on YouTube](https://youtu.be/jwWjvitz8Ng)

------

### Workflow:

  1. Create materials with Material Builder.
  2. Define geometry using Geometry Builder.
  3. Build universes and lattices.
  4. Export final geometry (geometry.xml).
  5. Configure simulation settings (particles, batches, source, energy).
  6. Optionally define tallies.
  7. Run OpenMC simulation via Run OpenMC.
------

### Design PINCELL usign  OpenMC-GUI tool:
[▶ Watch on YouTube](https://youtu.be/scdlaWJdpd8)

-----------------


### Outputs (saved in output/):

  - statepoint.h5
  - summary.h5
  - Remember all the xml, python and h5 files will be genereated in output directory

Energy distributions supported: OpenMC Default, Monoenergetic, Watt Spectrum, Maxwell Spectrum, Tabular.
---
### File Structure

```

openmc-gui-builder/
│
├── main.py                  # GUI launcher
├── modules/                 # GUI modules
│   ├── material_builder.py
│   ├── geometry_builder.py
│   ├── universe_builder.py
│   ├── lattice_builder.py
│   ├── final_geometry_builder.py
│   ├── settings_builder.py
│   ├── tallies_builder.py
│   └── run_openmc_builder.py
├── output/                  # Generated XML & simulation files
├── LICENSE
└── README.md

```

---
### 🤝 Contributing
We welcome contributions!

  - Fork the repository.
  - Create a new branch: git checkout -b feature-name
  - Commit your changes: git commit -m "Add feature"
  - Push to the branch: git push origin feature-name
  - Open a Pull Request.

<br><br>
---
### 📜 License

MIT License © 2025 Mahmudul Hasan

<br>


📬 Contact
Mahmudul Hasan  
Nuclear Engineering, Dhaka University, Bangladesh  
📧 mahmudul.du.ne8@gmail.com  
🔗 [LinkedIn](https://www.linkedin.com/in/mhm-111/)








