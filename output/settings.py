import openmc
import numpy as np

# ---------------- User-editable settings ----------------
settings = {'particles': 1000, 'batches': 50, 'inactive': 10, 'threads': None, 'seed': None, 'run_mode': 'Eigenvalue', 'cross_sections': None, 'source': {'type': 'Point', 'position': [0.0, 0.0, 0.0], 'radius': None, 'extent': None, 'energy': {'dist': 'OpenMC Default', 'param': '1e6'}}, 'outputs': {'statepoint': True, 'summary': True, 'restart': False}}

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

