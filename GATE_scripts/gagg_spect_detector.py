#!/usr/bin/env python3
"""
GAGG SPECT Detector Model
=========================
Custom GAGG scintillator SPECT detector that integrates with
opengate.contrib.spect.spect_config.SPECTConfig

This module follows the OpenGATE pattern for custom detector models,
similar to ge_discovery_nm670.py and siemens_intevo.py

Author: Claude
Date: 2025-11-21
"""

import json
import opengate as gate
from pathlib import Path
from box import Box
import math
import numpy as np
from scipy.spatial.transform import Rotation
from opengate.geometry.volumes import RepeatParametrisedVolume, HexagonVolume

# ==============================================================================
# Geometrical Parameters
# ==============================================================================

geometrical_parameters = None


def get_geometrical_parameters_filename():
    """Get path to geometric parameters JSON file"""
    return Path(__file__).parent / "gagg_spect_geometrical_parameters.json"


def get_geometrical_parameters():
    """
    Load GAGG SPECT geometric parameters from JSON file

    Returns:
    --------
    Box : Parameters as attribute-accessible dictionary
    """
    global geometrical_parameters
    if geometrical_parameters is None:
        filename = get_geometrical_parameters_filename()
        with open(filename) as json_file:
            geometrical_parameters = json.load(json_file)
            geometrical_parameters = Box(geometrical_parameters)
    return geometrical_parameters


def get_default_size_and_spacing(fov_preset="small_animal"):
    """
    Get default projection size and spacing based on detector array

    Parameters:
    -----------
    fov_preset : str
        FOV preset name (small_animal, medium, large_clinical)

    Returns:
    --------
    tuple : (size, spacing) where size is [nx, ny] and spacing is [sx, sy] in mm
    """
    params = get_geometrical_parameters()

    # Size matches crystal array
    size = [params.crystal_array_size_x, params.crystal_array_size_y]

    # Spacing = crystal_size + gap
    pixel_pitch = params.crystal_size_x_mm + params.crystal_spacing_mm
    spacing = [pixel_pitch, pixel_pitch]

    return size, spacing


# ==============================================================================
# Materials
# ==============================================================================

def add_materials(sim):
    """
    Add materials required for GAGG SPECT detector

    Parameters:
    -----------
    sim : gate.Simulation
        OpenGATE simulation object
    """
    # Check for local GateMaterials.db
    materials_db = Path(__file__).parent / "GateMaterials.db"

    if materials_db.exists():
        if str(materials_db) not in sim.volume_manager.material_database.filenames:
            sim.volume_manager.add_material_database(str(materials_db))
    else:
        # Use default GATE materials (basic materials should be available)
        pass


# ==============================================================================
# Detector Geometry
# ==============================================================================

def add_spect_head(
    sim,
    name="gagg_spect",
    collimator_type="pinhole",
    debug=False,
    params=None
):
    """
    Create GAGG SPECT detector head geometry

    Parameters:
    -----------
    sim : gate.Simulation
        OpenGATE simulation object
    name : str
        Name for the detector head
    collimator_type : str
        "pinhole" or "parallel"
    debug : bool
        Enable debug mode with reduced geometry
    params : dict
        Override parameters (if None, uses default from JSON)

    Returns:
    --------
    tuple : (head_volume, collimator_volume, crystal_volume)
    """
    if params is None:
        params = get_geometrical_parameters()

    mm = gate.g4_units.mm
    cm = gate.g4_units.cm

    # Add materials
    add_materials(sim)

    # Calculate dimensions
    detector_x = params.detector_size_x_mm * mm
    detector_y = params.detector_size_y_mm * mm

    collimator_thickness = params.collimator_thickness_mm * mm
    crystal_thickness = params.crystal_thickness_mm * mm
    backside_thickness = params.backside_thickness_mm * mm
    shielding_thickness = params.shielding_thickness_mm * mm

    head_depth = (
        collimator_thickness +
        crystal_thickness +
        backside_thickness +
        shielding_thickness * 2
    )

    head_size_x = detector_x + 10 * mm
    head_size_y = detector_y + 10 * mm

    # Colors
    white = [1, 1, 1, 0.1]
    gray = [0.1, 0.1, 0.1, 1]
    yellow = [1, 1, 0, 0.8]
    blue = [0.5, 0.5, 1, 0.8]
    green = [0, 1, 0, 0.8]
    red = [1, 0, 0, 0.3]

    # 1. Main head box
    head = sim.add_volume("Box", name)
    head.material = "G4_AIR"
    head.size = [head_size_x, head_size_y, head_depth]
    head.color = white

    # 2. Collimator (at front)
    if collimator_type:
        if collimator_type == "pinhole":
            collimator = add_pinhole_collimator(sim, name, head, params)
        elif collimator_type == "parallel":
            collimator = add_parallel_collimator(sim, name, head, params, debug)
        else:
            raise ValueError(f"Unknown collimator type: {collimator_type}")
    else:
        collimator = None

    # 3. Lead shielding box
    shielding = sim.add_volume("Box", f"{name}_shielding")
    shielding.mother = head.name
    shielding_depth = head_depth - collimator_thickness - 5 * mm
    shielding.size = [head_size_x - 5 * mm, head_size_y - 5 * mm, shielding_depth]
    shielding_z = -head_depth / 2 + shielding_depth / 2
    shielding.translation = [0, 0, shielding_z]
    shielding.material = params.shielding_material
    shielding.color = gray

    # 4. Shielding interior (air cavity)
    interior = sim.add_volume("Box", f"{name}_interior")
    interior.mother = shielding.name
    interior.size = [
        shielding.size[0] - 2 * shielding_thickness,
        shielding.size[1] - 2 * shielding_thickness,
        shielding.size[2] - shielding_thickness,  # Back wall only
    ]
    interior.translation = [0, 0, shielding_thickness / 2]
    interior.material = "G4_AIR"
    interior.color = red

    # 5. Crystal (sensitive detector)
    crystal = add_crystal(sim, name, interior, params, debug)

    # 6. Backside (PMT/Electronics)
    backside = sim.add_volume("Box", f"{name}_backside")
    backside.mother = interior.name
    backside.size = [detector_x, detector_y, backside_thickness]
    crystal_module_z = interior.size[2] / 2 - crystal_thickness / 2
    backside_z = crystal_module_z - crystal_thickness / 2 - backside.size[2] / 2
    backside.translation = [0, 0, backside_z]
    backside.material = params.backside_material
    backside.color = blue

    return head, collimator, crystal


def add_crystal(sim, head_name, parent_volume, params, debug=False):
    """
    Add GAGG crystal array

    Parameters:
    -----------
    sim : gate.Simulation
        OpenGATE simulation object
    head_name : str
        Name of the detector head
    parent_volume : Volume
        Parent volume for crystal module
    params : Box
        Geometric parameters
    debug : bool
        Use reduced array size for debugging

    Returns:
    --------
    Volume : Crystal volume
    """
    mm = gate.g4_units.mm

    # Crystal dimensions
    crystal_x = params.crystal_size_x_mm * mm
    crystal_y = params.crystal_size_y_mm * mm
    crystal_z = params.crystal_thickness_mm * mm

    # Array parameters
    if debug:
        # Reduced size for faster testing
        array_nx = 20
        array_ny = 20
    else:
        array_nx = params.crystal_array_size_x
        array_ny = params.crystal_array_size_y

    # Pixel pitch
    pitch_x = (params.crystal_size_x_mm + params.crystal_spacing_mm) * mm
    pitch_y = (params.crystal_size_y_mm + params.crystal_spacing_mm) * mm

    # Crystal module container
    module_name = f"{head_name}_crystal_module"
    module = sim.add_volume("Box", module_name)
    module.mother = parent_volume.name
    module.size = [array_nx * pitch_x, array_ny * pitch_y, crystal_z]
    # Position near front of interior
    module_z = parent_volume.size[2] / 2 - module.size[2] / 2
    module.translation = [0, 0, module_z]
    module.material = "G4_AIR"
    module.color = [1, 1, 0, 0.3]

    # Individual crystal (will be repeated)
    crystal_name = f"{head_name}_crystal"
    crystal = sim.add_volume("Box", crystal_name)
    crystal.mother = module.name
    crystal.size = [crystal_x, crystal_y, crystal_z]
    crystal.material = params.crystal_material
    crystal.color = [0, 1, 0, 0.8]

    # Repeat array
    repeat = gate.geometry.utility.repeat_array(
        repeat_vector=[pitch_x, pitch_y, 0],
        repeat_number=[array_nx, array_ny, 1]
    )
    crystal.repeaters.append(repeat)

    return crystal


def add_pinhole_collimator(sim, head_name, head_volume, params):
    """
    Add pinhole collimator

    Parameters:
    -----------
    sim : gate.Simulation
        OpenGATE simulation object
    head_name : str
        Name of the detector head
    head_volume : Volume
        Parent head volume
    params : Box
        Geometric parameters

    Returns:
    --------
    Volume : Collimator volume
    """
    mm = gate.g4_units.mm

    detector_x = params.detector_size_x_mm * mm
    detector_y = params.detector_size_y_mm * mm
    thickness = params.collimator_thickness_mm * mm

    # Collimator container
    colli_name = f"{head_name}_collimator"
    collimator = sim.add_volume("Box", colli_name)
    collimator.mother = head_volume.name
    collimator.size = [detector_x + 5 * mm, detector_y + 5 * mm, thickness]

    # Position at front of head
    colli_z = head_volume.size[2] / 2 - collimator.size[2] / 2 - 0.5 * mm
    collimator.translation = [0, 0, colli_z]
    collimator.material = params.collimator_material
    collimator.color = [1, 0.7, 0.7, 1]

    # Pinhole aperture (conical section)
    pinhole = sim.add_volume("Cons", f"{head_name}_pinhole")
    pinhole.mother = colli_name
    pinhole.rmin1 = 0
    pinhole.rmax1 = params.pinhole_diameter_mm / 2.0 * mm
    pinhole.rmin2 = 0
    # Exit diameter based on opening angle
    opening_angle_rad = np.deg2rad(params.pinhole_opening_angle_deg)
    exit_radius = params.pinhole_diameter_mm / 2.0 + thickness * np.tan(opening_angle_rad / 2)
    pinhole.rmax2 = exit_radius * mm
    pinhole.dz = thickness / 2.0  # Cons uses half-length
    pinhole.sphi = 0
    pinhole.dphi = 360 * gate.g4_units.deg
    pinhole.translation = [0, 0, 0]
    pinhole.material = "G4_AIR"
    pinhole.color = [0, 0, 1, 0.5]

    return collimator


def add_parallel_collimator(sim, head_name, head_volume, params, debug=False):
    """
    Add parallel-hole collimator with hexagonal holes

    Parameters:
    -----------
    sim : gate.Simulation
        OpenGATE simulation object
    head_name : str
        Name of the detector head
    head_volume : Volume
        Parent head volume
    params : Box
        Geometric parameters
    debug : bool
        Use reduced hole count for debugging

    Returns:
    --------
    Volume : Collimator volume
    """
    mm = gate.g4_units.mm

    detector_x = params.detector_size_x_mm * mm
    detector_y = params.detector_size_y_mm * mm
    hole_length = params.parallel_hole_length_mm * mm

    # Collimator container
    colli_name = f"{head_name}_collimator"
    collimator = sim.add_volume("Box", colli_name)
    collimator.mother = head_volume.name
    collimator.size = [detector_x + 5 * mm, detector_y + 5 * mm, hole_length]

    # Position at front of head
    colli_z = head_volume.size[2] / 2 - collimator.size[2] / 2 - 0.5 * mm
    collimator.translation = [0, 0, colli_z]
    collimator.material = params.collimator_material
    collimator.color = [1, 0.7, 0.7, 1]

    # Hexagonal holes (repeated pattern)
    hole_name = f"{head_name}_colli_hole"
    hole = sim.add_volume("Hexagon", hole_name)
    hole.mother = colli_name
    hole.height = hole_length
    hole.radius = params.parallel_hole_diameter_mm / 2.0 * mm
    hole.material = "G4_AIR"
    hole.color = [0, 0, 0, 0]
    hole.build_physical_volume = False  # Prototype for repeater

    # Hexagonal close-pack pattern
    septa = params.parallel_septa_thickness_mm * mm
    step_x = 3.0 * hole.radius + 2.0 * septa
    step_y = math.sqrt(3) * hole.radius + 2.0 * septa

    if debug:
        nx, ny = 10, 10
    else:
        nx = int(collimator.size[0] / step_x)
        ny = int(collimator.size[1] / step_y)

    holep = RepeatParametrisedVolume(repeated_volume=hole)
    holep.linear_repeat = [nx, ny, 1]
    holep.translation = [step_x, step_y, 0]

    # Second grid with offset (hexagonal packing)
    holep.offset_nb = 2
    holep.offset = [step_x / 2.0, step_y / 2.0, 0]

    sim.volume_manager.add_volume(holep)

    return collimator


# ==============================================================================
# Multi-Head Setup
# ==============================================================================

def add_gagg_spect_heads(
    sim,
    number_of_heads=3,
    collimator_type="pinhole",
    fov_preset="small_animal",
    debug=False,
    params=None
):
    """
    Add multiple GAGG SPECT detector heads in ring configuration

    Parameters:
    -----------
    sim : gate.Simulation
        OpenGATE simulation object
    number_of_heads : int
        Number of detector heads (1-4)
    collimator_type : str
        "pinhole" or "parallel"
    fov_preset : str
        FOV preset name (small_animal, medium, large_clinical)
    debug : bool
        Enable debug mode
    params : dict
        Override parameters

    Returns:
    --------
    tuple : (list of heads, list of crystals)
    """
    if params is None:
        params = get_geometrical_parameters()

    cm = gate.g4_units.cm

    # Get FOV configuration
    fov_config = params.fov_presets[fov_preset]
    detector_radius = fov_config.detector_radius_cm * cm

    # Head angles
    if number_of_heads == 1:
        angles = [0.0]
    elif number_of_heads == 2:
        angles = [0.0, 180.0]
    elif number_of_heads == 3:
        angles = [0.0, 120.0, 240.0]
    elif number_of_heads == 4:
        angles = [0.0, 90.0, 180.0, 270.0]
    else:
        raise ValueError(f"Number of heads must be 1-4, got {number_of_heads}")

    heads = []
    crystals = []

    for i, angle in enumerate(angles):
        head_name = f"gagg_spect_head_{i}"

        # Create head
        head, collimator, crystal = add_spect_head(
            sim, head_name, collimator_type, debug, params
        )

        # Position in ring
        angle_rad = np.deg2rad(angle)
        x = detector_radius * np.cos(angle_rad)
        y = detector_radius * np.sin(angle_rad)

        # Rotation: point collimator toward center
        rot = Rotation.from_euler("z", angle + 180, degrees=True)

        head.translation = [x, y, 0]
        head.rotation = rot.as_matrix()

        heads.append(head)
        crystals.append(crystal)

    return heads, crystals


# ==============================================================================
# Digitizer Setup
# ==============================================================================

def add_gagg_digitizer(
    sim,
    crystal_name,
    name=None,
    params=None,
    output_filename=None
):
    """
    Add digitizer chain for GAGG detector

    Parameters:
    -----------
    sim : gate.Simulation
        OpenGATE simulation object
    crystal_name : str
        Name of crystal volume
    name : str
        Digitizer name
    params : Box
        Geometric parameters
    output_filename : str
        Output file path for projections

    Returns:
    --------
    Digitizer : Configured digitizer object
    """
    if params is None:
        params = get_geometrical_parameters()

    if name is None:
        name = crystal_name

    keV = gate.g4_units.keV
    mm = gate.g4_units.mm

    # Get projection parameters
    size, spacing = get_default_size_and_spacing()

    # Hits collection
    hits = sim.add_actor("DigitizerHitsCollectionActor", f"{name}_hits")
    hits.attached_to = crystal_name
    hits.output_filename = output_filename or f"{name}_hits.root"
    hits.attributes = [
        "PostPosition",
        "TotalEnergyDeposit",
        "GlobalTime",
        "PreStepUniqueVolumeID",
    ]

    # Singles (adder)
    singles = sim.add_actor("DigitizerAdderActor", f"{name}_singles")
    singles.attached_to = crystal_name
    singles.input_digi_collection = hits.name
    singles.policy = "EnergyWinnerPosition"

    # Energy blurring
    blur = sim.add_actor("DigitizerEnergyBlurringActor", f"{name}_eblur")
    blur.attached_to = crystal_name
    blur.input_digi_collection = singles.name
    blur.blur_fwhm = params.energy_resolution_fwhm
    blur.blur_reference_value = params.energy_reference_keV * keV

    # Energy window
    channel_name = f"{name}_channel"
    ewin = sim.add_actor("DigitizerEnergyWindowsActor", f"{name}_ewin")
    ewin.attached_to = crystal_name
    ewin.input_digi_collection = blur.name
    ewin.channels = [
        {
            "name": channel_name,
            "min": params.energy_window_lower_keV * keV,
            "max": params.energy_window_upper_keV * keV,
        }
    ]

    # Projection
    proj = sim.add_actor("DigitizerProjectionActor", f"{name}_projection")
    proj.attached_to = crystal_name
    proj.input_digi_collections = [channel_name]
    proj.size = size
    proj.spacing = [spacing[0] * mm, spacing[1] * mm]
    proj.output_filename = output_filename or f"{name}_projection.mhd"

    return hits, singles, blur, ewin, proj


# ==============================================================================
# Example Usage
# ==============================================================================

if __name__ == "__main__":
    print("GAGG SPECT Detector Module")
    print("=" * 70)

    # Load parameters
    params = get_geometrical_parameters()
    print(f"\nDetector: {params.detector_name}")
    print(f"Crystal: {params.crystal_size_x_mm} × {params.crystal_size_y_mm} × {params.crystal_thickness_mm} mm")
    print(f"Array: {params.crystal_array_size_x} × {params.crystal_array_size_y}")
    print(f"Collimator: {params.collimator_type}")

    print(f"\nFOV Presets:")
    for preset_name, preset in params.fov_presets.items():
        print(f"  {preset_name}: {preset.description}")
        print(f"    Radius: {preset.fov_radius_cm} cm, Detector @ {preset.detector_radius_cm} cm")

    print("\nTo use this detector with SPECTConfig, see the example script.")
