import openmc
from geometry import *  # import all previously defined universes/cells

geometry = openmc.Geometry(universes['root_univere'])
geometry.export_to_xml('output/geometry.xml')
print('Final geometry created with universe: root_univere')
