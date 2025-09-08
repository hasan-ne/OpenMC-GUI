import openmc

# Generated OpenMC materials file

import openmc

# Generated OpenMC materials file

import openmc

# Generated OpenMC materials file

# Material: uo2
uo2 = openmc.Material(name='uo2')
uo2.set_density('g/cm3', 10.0)
uo2.add_nuclide('U235', 0.03)
uo2.add_nuclide('U238', 0.97)
uo2.add_nuclide('O16', 2.0)
uo2.depletable = False

# Material: zirconium
zirconium = openmc.Material(name='zirconium')
zirconium.set_density('g/cm3', 6.6)
zirconium.add_element('Zr', 1.0)
zirconium.depletable = False

# Material: water
water = openmc.Material(name='water')
water.set_density('g/cm3', 1.0)
water.add_nuclide('H1', 2.0)
water.add_nuclide('O16', 1.0)
water.add_s_alpha_beta('c_H_in_H2O')
water.depletable = False

materials_file = openmc.Materials([uo2, zirconium, water])
materials_file.export_to_xml('materials.xml')
