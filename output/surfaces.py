import openmc

fuel_outer_radius = openmc.ZCylinder(r=0.39)
clad_inner_radius = openmc.ZCylinder(r=0.40)
clad_outer_radius = openmc.ZCylinder(r=0.46)
left = openmc.XPlane(x0=-0.63, boundary_type='reflective')
right = openmc.XPlane(x0=0.63, boundary_type='reflective')
down = openmc.YPlane(y0=-0.63, boundary_type='reflective')
up = openmc.YPlane(y0=0.63, boundary_type='reflective')

# Surfaces are used in regions, no direct XML export.
