import openmc
import os

def load_materials_from_xml(xml_path="materials.xml"):
    """Load only user-defined materials from XML."""
    if not os.path.exists(xml_path):
        return {}

    try:
        mats = openmc.Materials.from_xml(xml_path)
        return {mat.name: mat for mat in mats if mat.name}  # skip None/defaults
    except Exception as e:
        print(f"Failed to load materials from {xml_path}: {e}")
        return {}
