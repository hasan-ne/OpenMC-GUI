import openmc
from surfaces import *
from materials import *

fuel = openmc.Cell(name='fuel', fill=uo2, region=-fuel_outer_radius)
clad = openmc.Cell(name='clad', fill=zirconium, region=+clad_inner_radius & -clad_outer_radius)
gap = openmc.Cell(name='gap', fill=uo2, region=+fuel_outer_radius & - clad_inner_radius)
water = openmc.Cell(name='water', fill=water, region=+left & -right & +down & -up)

universes = {}
universes['root_univere'] = openmc.Universe(name='root_univere')
universes['root_univere'].add_cell(fuel)
universes['root_univere'].add_cell(clad)
universes['root_univere'].add_cell(gap)
universes['root_univere'].add_cell(water)

geometry = openmc.Geometry([fuel, clad, gap, water])
