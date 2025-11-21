#!/usr/bin/env python3
"""
Geometry 3: Animal SPECT System
===============================
Based on GE Discovery NM670 logic but scaled down for animal imaging.
- FOV: ~10 cm
- Heads: 2 (Parallel opposed)
- Crystal: NaI(Tl)
- Collimator: Parallel Hole (LEHR-like)

"""

import opengate as gate
import opengate.contrib.spect.spect_helpers as spect_helpers
from opengate.geometry.volumes import RepeatParametrisedVolume, HexagonVolume
from opengate.geometry.utility import get_transform_orbiting
from scipy.spatial.transform import Rotation
import pathlib
import math
import click


# ==============================================================================
# CONFIGURATION
# ==============================================================================

# Dimensions for Animal SPECT
HEAD_SIZE_X = 20.0 * gate.g4_units.cm
HEAD_SIZE_Y = 15.0 * gate.g4_units.cm
HEAD_LENGTH = 15.0 * gate.g4_units.cm

CRYSTAL_SIZE_X = 16.0 * gate.g4_units.cm
CRYSTAL_SIZE_Y = 12.0 * gate.g4_units.cm
CRYSTAL_THICKNESS = 0.9525 * gate.g4_units.cm  # 3/8 inch

SHIELDING_THICKNESS = 0.5 * gate.g4_units.cm

# Collimator parameters (High Resolution for small animals)
COLLI_HOLE_RADIUS = 0.15 * gate.g4_units.cm  # 3.0mm diameter
COLLI_SEPTA = 0.05 * gate.g4_units.cm
COLLI_HEIGHT = 1.5 * gate.g4_units.cm

# ==============================================================================
# GEOMETRY FUNCTIONS
# ==============================================================================

def add_materials(sim):
    # Use local GateMaterials.db if available, otherwise standard
    f = pathlib.Path(__file__).parent.resolve()
    fdb = f / "GateMaterials.db"
    if fdb.exists():
        if str(fdb) not in sim.volume_manager.material_database.filenames:
            sim.volume_manager.add_material_database(str(fdb))
    else:
        # Fallback or add standard database
        pass

def add_animal_spect_head(sim, name="spect_head", collimator_type="lehr", debug=False):
    """
    Creates a single SPECT head scaled for animal imaging.
    """
    cm = gate.g4_units.cm
    mm = gate.g4_units.mm
    
    # Colors
    white = [1, 1, 1, 0.1]
    gray = [0.1, 0.1, 0.1, 1]
    yellow = [1, 1, 0, 1]
    blue = [0.5, 0.5, 1, 0.8]
    red = [1, 0, 0, 0.5]
    
    # 1. Main Head Box
    head = sim.add_volume("Box", name)
    head.material = "Air" # G4_AIR
    head.size = [HEAD_SIZE_X, HEAD_SIZE_Y, HEAD_LENGTH]
    head.color = white
    
    # 2. Shielding (Lead Box)
    # Shielding covers the back and sides, leaving front open for collimator
    shielding = sim.add_volume("Box", f"{name}_shielding")
    shielding.mother = head.name
    # Make shielding shorter to accommodate collimator at front
    shielding_length = HEAD_LENGTH - COLLI_HEIGHT - 0.5*cm
    shielding.size = [HEAD_SIZE_X - 0.5*cm, HEAD_SIZE_Y - 0.5*cm, shielding_length]
    # Shift shielding back
    shielding_z_pos = -HEAD_LENGTH/2 + shielding_length/2
    shielding.translation = [0, 0, shielding_z_pos]
    shielding.material = "Lead"
    shielding.color = gray

    # 2.1 Shielding Interior (Air)
    # Create a hollow box (shell) by placing an Air volume inside the Lead volume
    # Open at the front (+Z), closed at the back (-Z) and sides
    shielding_interior = sim.add_volume("Box", f"{name}_shielding_interior")
    shielding_interior.mother = shielding.name
    shielding_interior.size = [
        shielding.size[0] - 2 * SHIELDING_THICKNESS,
        shielding.size[1] - 2 * SHIELDING_THICKNESS,
        shielding.size[2] - SHIELDING_THICKNESS # Only back wall has thickness
    ]
    # Shift interior forward so front faces align (creating back wall)
    shielding_interior.translation = [0, 0, SHIELDING_THICKNESS /2.0]
    shielding_interior.material = "Air"
    shielding_interior.color = red # Invisible-ish
    
    # 3. Crystal (NaI)
    crystal = sim.add_volume("Box", f"{name}_crystal")
    crystal.mother = shielding_interior.name
    crystal.size = [CRYSTAL_SIZE_X, CRYSTAL_SIZE_Y, CRYSTAL_THICKNESS]
    
    # Position crystal near the front of shielding interior
    # Front of interior is at +shielding_interior.size[2]/2
    crystal.translation = [0, 0, shielding_interior.size[2]/2 - CRYSTAL_THICKNESS/2 ]
    crystal.material = "NaI"
    crystal.color = yellow
    
    # 4. Backside (PMT/Electronics) - Simplified
    backside = sim.add_volume("Box", f"{name}_backside")
    backside.mother = shielding_interior.name
    backside.size = [CRYSTAL_SIZE_X, CRYSTAL_SIZE_Y, 5*cm]
    # Place backside behind crystal
    backside_z = crystal.translation[2] - CRYSTAL_THICKNESS/2 - backside.size[2]/2
    backside.translation = [0, 0, backside_z]
    backside.material = "Glass"
    backside.color = blue

    # 5. Collimator
    colli = None
    if collimator_type:
        colli = add_animal_collimator(sim, name, head, collimator_type, debug)
        
    return head, colli, crystal

def add_animal_collimator(sim, name, head, collimator_type, debug):
    """
    Adds a parallel hole collimator.
    """
    cm = gate.g4_units.cm
    mm = gate.g4_units.mm
    
    # Collimator Container
    colli_name = f"{name}_collimator"
    colli = sim.add_volume("Box", colli_name)
    colli.mother = head.name
    colli.size = [HEAD_SIZE_X - 1*cm, HEAD_SIZE_Y - 1*cm, COLLI_HEIGHT]
    
    # Place at the very front of the head box
    # Head front is at +HEAD_LENGTH/2
    colli_z_pos = HEAD_LENGTH/2 - COLLI_HEIGHT/2 - 0.1*mm
    colli.translation = [0, 0, colli_z_pos]
    colli.material = "Lead"
    colli.color = [1, 0.7, 0.7, 1] # Reddish
    
    # Hole (Hexagon)
    hole_name = f"{name}_colli_hole"
    hole = sim.add_volume("Hexagon", hole_name)
    hole.mother = colli_name
    hole.height = COLLI_HEIGHT
    hole.radius = COLLI_HOLE_RADIUS
    hole.material = "Air"
    hole.color = [0, 0, 0, 0]
    hole.build_physical_volume = False # Prototype for repeater
    
    # Repeater for hexagonal close pack
    # ---------------------------------
    # Form by two grid repeaters, centers of hexegons are closest pack
    # when 1/sqrt(3) apart. Second repeater grid is offset by 1/2 steps

    step_x = 3.0 * (COLLI_HOLE_RADIUS) + 2.0 * COLLI_SEPTA
    step_y = math.sqrt(3) * (COLLI_HOLE_RADIUS) + 2.0 * COLLI_SEPTA 
    
    nx = int(colli.size[0] / step_x)
    ny = int(colli.size[1] / step_y)
    
    # if debug:
        # print(f"{[COLLI_HOLE_RADIUS, COLLI_SEPTA] = }")
        # nx, ny = 3, 3 # Fast debug
        
    holep = RepeatParametrisedVolume(repeated_volume=hole)
    holep.linear_repeat = [nx, ny, 1]
    holep.translation = [step_x, step_y, 0] # Start offset handled by repeater centering usually
    
    # Second grid with offsets
    holep.offset_nb = 2    
    holep.offset = [step_x / 2.0, step_y / 2.0, 0]
    
    sim.volume_manager.add_volume(holep)
    
    return colli

def add_animal_spect_two_heads(sim, radius=10*gate.g4_units.cm, debug=False):
    """
    Adds two SPECT heads at 0 and 180 degrees.
    """
    # Head 1
    h1, c1, cry1 = add_animal_spect_head(sim, "head1", collimator_type="lehr", debug=debug)
    
    # Head 2
    h2, c2, cry2 = add_animal_spect_head(sim, "head2", collimator_type="lehr", debug=debug)
    
    # Position them
    r1 = Rotation.from_euler("x", -90, degrees=True)
    h1.translation = [0, -radius, 0]
    h1.rotation = r1.as_matrix()
    
    # Head 2
    # Position: [0, -radius, 0]
    # Rotation: Point +Z to [0,0,0].
    # Rotate +90 X: +Z becomes +Y.
    r2 = Rotation.from_euler("x", 90, degrees=True)
    h2.translation = [0, radius, 0]
    h2.rotation = r2.as_matrix()
    
    return [h1, h2], [cry1, cry2]

def create_simulation(debug=False):
    sim = gate.Simulation()
    
    # 1. Materials
    add_materials(sim)
    sim.check_volumes_overlap = True
    
    # 2. World
    sim.world.size = [100 * gate.g4_units.cm, 100 * gate.g4_units.cm, 100 * gate.g4_units.cm]
    sim.world.material = "Air"
    sim.world.visible = False
    sim.world.color = [1, 0, 0, 0]
    
    # 3. Geometry
    # Radius for 10cm FOV (5cm radius). 
    # Head needs to be outside FOV. 
    # Radius = 5cm (FOV) + 2cm (Clearance) + Head_Half_Length?
    # No, radius usually refers to distance from center to collimator face.
    # Our collimator face is at +HEAD_LENGTH/2 in head frame.
    # If head center is at R, face is at R - HEAD_LENGTH/2 (if facing in).
    # We want Face at ~6-7 cm from center.
    # So Center R = 7cm + HEAD_LENGTH/2 = 7 + 7.5 = 14.5 cm.
    
    face_distance = 7.0 * gate.g4_units.cm # 2cm clearance from 10cm FOV
    center_radius = face_distance + HEAD_LENGTH / 2.0
    
    heads, crystals = add_animal_spect_two_heads(sim, radius=center_radius, debug=debug)
    
    # 4. Physics
    sim.physics_manager.physics_list_name = "G4EmStandardPhysics_option4"
    
    # # 5. Source (Simple point source for testing)
    source = sim.add_source("GenericSource", "point_source")
    source.particle = "gamma"
    source.energy.mono = 140.5 * gate.g4_units.keV # Tc99m
    source.activity = 1000 * gate.g4_units.Bq
    source.position.type = "sphere"
    source.position.radius = 1 * gate.g4_units.cm
    source.direction.type = "iso"
    
    # 6. Digitizer / Actors
    for i, cry in enumerate(crystals):
        print(i)
        # Hits
        hc = sim.add_actor("DigitizerHitsCollectionActor", f"Hits_{i}")
        hc.attached_to = cry.name
        hc.output_filename = f"hits_{i}.root"
        hc.attributes = ["PostPosition", "TotalEnergyDeposit", "GlobalTime", "PreStepUniqueVolumeID"]
        
        # Singles (Adder)
        sc = sim.add_actor("DigitizerAdderActor", f"Singles_{i}")
        sc.attached_to = cry.name
        sc.input_digi_collection = hc.name
        sc.policy = "EnergyWinnerPosition"
        
        # Energy Window
        channel_name = f"Tc99m_{i}"
        cc = sim.add_actor("DigitizerEnergyWindowsActor", f"EnergyWin_{i}")
        cc.attached_to = cry.name
        cc.input_digi_collection = sc.name
        cc.channels = [{"name": channel_name, "min": 126 * gate.g4_units.keV, "max": 154 * gate.g4_units.keV}]
        
        # Projection
        proj = sim.add_actor("DigitizerProjectionActor", f"Projection_{i}")
        proj.attached_to = cry.name
        proj.input_digi_collections = [channel_name]
        proj.size = [128, 128]
        proj.spacing = [2*gate.g4_units.mm, 2*gate.g4_units.mm]
        proj.output_filename = f"projection_{i}.mhd"

    # 7. Simulation parameters
    sim.run_timing_intervals = [[0, 300 * gate.g4_units.second]]
    
    return sim


@click.command()
@click.option('--visu', is_flag=True, help='Enable visualization')
@click.option('--visu-type', default='vrml', type=click.Choice(['vrml', 'qt']), help='Visualization type')
def main(visu, visu_type):
    sim = create_simulation(debug=True)
    
    # Visualization
    sim.visu = visu
    sim.visu_type = visu_type
    
    sim.run() 

if __name__ == "__main__":
    main()
