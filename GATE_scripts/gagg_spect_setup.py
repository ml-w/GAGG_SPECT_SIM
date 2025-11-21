#!/usr/bin/env python3
"""
GAGG SPECT Geometry Setup
==========================
Uses gagg_spect_config.py to build configurable SPECT system geometry.

Author: Claude
Date: 2025-11-21
"""

import opengate as gate
from opengate.geometry.volumes import RepeatParametrisedVolume, HexagonVolume
from scipy.spatial.transform import Rotation
import pathlib
import math
import numpy as np
from gagg_spect_config import (
    SPECTConfig,
    ScintillatorConfig,
    CollimatorConfig,
    FOVConfig,
    DetectorConfig,
    AcquisitionConfig,
    SourceConfig,
    DigitizerConfig,
)


# ==============================================================================
# Material Setup
# ==============================================================================

def add_materials(sim, config: SPECTConfig):
    """
    Add material database to simulation

    Parameters:
    -----------
    sim : gate.Simulation
        OpenGATE simulation object
    config : SPECTConfig
        Configuration containing materials database path
    """
    # Check for local materials database
    if config.materials_database:
        db_path = pathlib.Path(config.materials_database)
    else:
        # Look for Materials.xml in same directory
        f = pathlib.Path(__file__).parent.resolve()
        db_path = f / "Materials.xml"

    if db_path.exists():
        if str(db_path) not in sim.volume_manager.material_database.filenames:
            sim.volume_manager.add_material_database(str(db_path))
            print(f"✅ Loaded material database: {db_path}")
    else:
        print(f"⚠️  Material database not found at: {db_path}")
        print(f"   Using default GATE materials")


# ==============================================================================
# Detector Head Geometry
# ==============================================================================

def add_spect_head(sim, config: SPECTConfig, head_name: str):
    """
    Create a single SPECT detector head based on configuration

    Parameters:
    -----------
    sim : gate.Simulation
        OpenGATE simulation object
    config : SPECTConfig
        System configuration
    head_name : str
        Name for this detector head

    Returns:
    --------
    tuple : (head_volume, collimator_volume, crystal_volume)
    """
    cm = gate.g4_units.cm
    mm = gate.g4_units.mm

    scint_cfg = config.detector.scintillator
    colli_cfg = config.detector.collimator

    # Calculate head dimensions based on detector array
    detector_x = scint_cfg.detector_size_x * mm  # Convert to GATE units
    detector_y = scint_cfg.detector_size_y * mm

    # Head box should contain collimator + crystal + backside + shielding
    head_depth = (
        colli_cfg.thickness +
        scint_cfg.crystal_thickness +
        config.detector.backside_thickness +
        config.detector.shielding_thickness * 2
    ) * mm

    head_size_x = detector_x + 10 * mm  # Add margin
    head_size_y = detector_y + 10 * mm

    # Colors
    white = [1, 1, 1, 0.1]
    gray = [0.1, 0.1, 0.1, 1]
    yellow = [1, 1, 0, 1]
    blue = [0.5, 0.5, 1, 0.8]
    green = [0, 1, 0, 0.8]
    red = [1, 0, 0, 0.5]

    # 1. Main Head Box
    head = sim.add_volume("Box", head_name)
    head.material = "Air"
    head.size = [head_size_x, head_size_y, head_depth]
    head.color = white

    # 2. Collimator
    collimator = None
    if colli_cfg.type == "pinhole":
        collimator = add_pinhole_collimator(sim, config, head_name, head)
    elif colli_cfg.type == "parallel":
        collimator = add_parallel_collimator(sim, config, head_name, head)
    else:
        print(f"⚠️  Unknown collimator type: {colli_cfg.type}")

    # 3. Shielding (Lead box)
    shielding = sim.add_volume("Box", f"{head_name}_shielding")
    shielding.mother = head.name
    shielding_thickness = config.detector.shielding_thickness * mm
    shielding_depth = head_depth - colli_cfg.thickness * mm - 5 * mm
    shielding.size = [head_size_x - 5 * mm, head_size_y - 5 * mm, shielding_depth]
    # Position behind collimator
    shielding_z = -head_depth / 2 + shielding_depth / 2
    shielding.translation = [0, 0, shielding_z]
    shielding.material = config.detector.shielding_material
    shielding.color = gray

    # 4. Shielding Interior (Air cavity)
    interior = sim.add_volume("Box", f"{head_name}_interior")
    interior.mother = shielding.name
    interior.size = [
        shielding.size[0] - 2 * shielding_thickness,
        shielding.size[1] - 2 * shielding_thickness,
        shielding.size[2] - shielding_thickness,  # Back wall only
    ]
    interior.translation = [0, 0, shielding_thickness / 2]
    interior.material = "Air"
    interior.color = red

    # 5. Crystal Module (contains crystal array)
    crystal_module = sim.add_volume("Box", f"{head_name}_crystal_module")
    crystal_module.mother = interior.name
    crystal_module.size = [detector_x, detector_y, scint_cfg.crystal_thickness * mm]
    # Position near front of interior
    crystal_z = interior.size[2] / 2 - crystal_module.size[2] / 2
    crystal_module.translation = [0, 0, crystal_z]
    crystal_module.material = "Air"
    crystal_module.color = yellow

    # 6. Individual Crystal (will be repeated)
    crystal = sim.add_volume("Box", f"{head_name}_crystal")
    crystal.mother = crystal_module.name
    crystal.size = [
        scint_cfg.crystal_size_x * mm,
        scint_cfg.crystal_size_y * mm,
        scint_cfg.crystal_thickness * mm,
    ]
    crystal.material = scint_cfg.material
    crystal.color = green

    # 7. Repeat Crystal Array
    crystal.repeaters.append(
        gate.geometry.utility.repeat_array(
            repeat_vector=[
                scint_cfg.pixel_pitch_x * mm,
                scint_cfg.pixel_pitch_y * mm,
                0,
            ],
            repeat_number=[scint_cfg.array_size_x, scint_cfg.array_size_y, 1],
        )
    )

    # 8. Backside (PMT/Electronics)
    backside = sim.add_volume("Box", f"{head_name}_backside")
    backside.mother = interior.name
    backside.size = [detector_x, detector_y, config.detector.backside_thickness * mm]
    # Position behind crystal
    backside_z = crystal_module.translation[2] - crystal_module.size[2] / 2 - backside.size[2] / 2
    backside.translation = [0, 0, backside_z]
    backside.material = config.detector.backside_material
    backside.color = blue

    return head, collimator, crystal


def add_pinhole_collimator(sim, config: SPECTConfig, head_name: str, head_volume):
    """Add pinhole collimator to detector head"""
    mm = gate.g4_units.mm
    colli_cfg = config.detector.collimator
    scint_cfg = config.detector.scintillator

    detector_x = scint_cfg.detector_size_x * mm
    detector_y = scint_cfg.detector_size_y * mm

    # Collimator container
    colli_name = f"{head_name}_collimator"
    collimator = sim.add_volume("Box", colli_name)
    collimator.mother = head_volume.name
    collimator.size = [detector_x + 5 * mm, detector_y + 5 * mm, colli_cfg.thickness * mm]

    # Position at front of head
    colli_z = head_volume.size[2] / 2 - collimator.size[2] / 2 - 0.5 * mm
    collimator.translation = [0, 0, colli_z]
    collimator.material = colli_cfg.material
    collimator.color = [1, 0.7, 0.7, 1]

    # Pinhole aperture (cone)
    pinhole = sim.add_volume("Cone", f"{head_name}_pinhole")
    pinhole.mother = colli_name
    pinhole.rmin1 = 0
    pinhole.rmax1 = colli_cfg.pinhole_diameter / 2.0 * mm
    pinhole.rmin2 = 0
    pinhole.rmax2 = colli_cfg.pinhole_diameter * mm  # Exit diameter
    pinhole.height = colli_cfg.thickness * mm
    pinhole.translation = [0, 0, 0]
    pinhole.material = "Air"
    pinhole.color = [0, 0, 1, 0.5]

    return collimator


def add_parallel_collimator(sim, config: SPECTConfig, head_name: str, head_volume):
    """Add parallel-hole collimator to detector head"""
    mm = gate.g4_units.mm
    colli_cfg = config.detector.collimator
    scint_cfg = config.detector.scintillator

    detector_x = scint_cfg.detector_size_x * mm
    detector_y = scint_cfg.detector_size_y * mm

    # Collimator container
    colli_name = f"{head_name}_collimator"
    collimator = sim.add_volume("Box", colli_name)
    collimator.mother = head_volume.name
    collimator.size = [
        detector_x + 5 * mm,
        detector_y + 5 * mm,
        colli_cfg.parallel_hole_length * mm,
    ]

    # Position at front of head
    colli_z = head_volume.size[2] / 2 - collimator.size[2] / 2 - 0.5 * mm
    collimator.translation = [0, 0, colli_z]
    collimator.material = colli_cfg.material
    collimator.color = [1, 0.7, 0.7, 1]

    # Hexagonal hole (will be repeated)
    hole_name = f"{head_name}_colli_hole"
    hole = sim.add_volume("Hexagon", hole_name)
    hole.mother = colli_name
    hole.height = colli_cfg.parallel_hole_length * mm
    hole.radius = colli_cfg.parallel_hole_diameter / 2.0 * mm
    hole.material = "Air"
    hole.color = [0, 0, 0, 0]
    hole.build_physical_volume = False  # Prototype for repeater

    # Hexagonal close-pack pattern
    step_x = 3.0 * hole.radius + 2.0 * colli_cfg.parallel_septa_thickness * mm
    step_y = math.sqrt(3) * hole.radius + 2.0 * colli_cfg.parallel_septa_thickness * mm

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
# Multi-Head Positioning
# ==============================================================================

def add_detector_heads(sim, config: SPECTConfig):
    """
    Add all detector heads with proper positioning

    Parameters:
    -----------
    sim : gate.Simulation
        OpenGATE simulation object
    config : SPECTConfig
        System configuration

    Returns:
    --------
    tuple : (list of head volumes, list of crystal volumes)
    """
    cm = gate.g4_units.cm
    heads = []
    crystals = []

    # Get head angles from configuration
    angles = config.detector.get_head_angles()
    radius = config.fov.detector_radius * cm

    for i, angle in enumerate(angles):
        head_name = f"head{i}"

        # Create head
        head, collimator, crystal = add_spect_head(sim, config, head_name)

        # Position head at specified angle
        # Convert angle to radians
        angle_rad = np.deg2rad(angle)

        # Position in XY plane
        x = radius * np.cos(angle_rad)
        y = radius * np.sin(angle_rad)

        # Rotation: point collimator face toward center
        # Head's local +Z should point toward origin
        rot = Rotation.from_euler("z", angle + 180, degrees=True)

        head.translation = [x, y, 0]
        head.rotation = rot.as_matrix()

        heads.append(head)
        crystals.append(crystal)

    print(f"✅ Added {len(heads)} detector heads at angles: {angles}")

    return heads, crystals


# ==============================================================================
# FOV Phantom
# ==============================================================================

def add_fov_phantom(sim, config: SPECTConfig):
    """
    Add FOV phantom (water cylinder for reference)

    Parameters:
    -----------
    sim : gate.Simulation
        OpenGATE simulation object
    config : SPECTConfig
        System configuration
    """
    cm = gate.g4_units.cm

    fov = sim.add_volume("Cylinder", "FOV")
    fov.rmax = config.fov.radius * cm
    fov.rmin = 0
    fov.height = config.fov.height * cm
    fov.material = "Water"
    fov.color = [0, 1, 1, 0.2]  # Cyan, transparent
    fov.translation = [0, 0, 0]

    print(f"✅ Added FOV phantom: {config.fov.name} (Ø{config.fov.diameter} cm × {config.fov.height} cm)")

    return fov


# ==============================================================================
# Source Setup
# ==============================================================================

def add_source(sim, config: SPECTConfig):
    """
    Add radioactive source based on configuration

    Parameters:
    -----------
    sim : gate.Simulation
        OpenGATE simulation object
    config : SPECTConfig
        System configuration
    """
    keV = gate.g4_units.keV
    Bq = gate.g4_units.Bq
    mm = gate.g4_units.mm

    src_cfg = config.source

    source = sim.add_source("GenericSource", src_cfg.isotope)
    source.particle = "gamma"
    source.energy.mono = src_cfg.energy * keV
    source.activity = src_cfg.activity * Bq

    # Position
    source.position.translation = [
        src_cfg.position[0] * mm,
        src_cfg.position[1] * mm,
        src_cfg.position[2] * mm,
    ]

    # Geometry type
    if src_cfg.geometry_type == "point":
        source.position.type = "point"
    elif src_cfg.geometry_type == "sphere":
        source.position.type = "sphere"
        source.position.radius = src_cfg.geometry_radius * mm
    elif src_cfg.geometry_type == "cylinder":
        source.position.type = "cylinder"
        source.position.radius = src_cfg.geometry_radius * mm
        source.position.height = src_cfg.geometry_height * mm

    # Isotropic emission
    source.direction.type = "iso"

    print(f"✅ Added source: {src_cfg.isotope} @ {src_cfg.energy} keV, "
          f"{src_cfg.activity:.2e} Bq, type={src_cfg.geometry_type}")

    return source


# ==============================================================================
# Digitizer Chain
# ==============================================================================

def add_digitizer(sim, config: SPECTConfig, crystals: list):
    """
    Add digitizer chain for each detector head

    Parameters:
    -----------
    sim : gate.Simulation
        OpenGATE simulation object
    config : SPECTConfig
        System configuration
    crystals : list
        List of crystal volumes
    """
    keV = gate.g4_units.keV
    mm = gate.g4_units.mm

    digi_cfg = config.digitizer

    for i, crystal in enumerate(crystals):
        # Hits collection
        hits = sim.add_actor("DigitizerHitsCollectionActor", f"Hits_{i}")
        hits.attached_to = crystal.name
        hits.output_filename = f"{config.output_dir}/hits_{i}.root"
        hits.attributes = [
            "PostPosition",
            "TotalEnergyDeposit",
            "GlobalTime",
            "PreStepUniqueVolumeID",
        ]

        # Singles (Adder)
        singles = sim.add_actor("DigitizerAdderActor", f"Singles_{i}")
        singles.attached_to = crystal.name
        singles.input_digi_collection = hits.name
        singles.policy = "EnergyWinnerPosition"

        # Energy Blurring
        blur = sim.add_actor("DigitizerEnergyBlurringActor", f"EnergyBlur_{i}")
        blur.attached_to = crystal.name
        blur.input_digi_collection = singles.name
        blur.blur_fwhm = digi_cfg.energy_resolution
        blur.blur_reference_value = digi_cfg.energy_reference * keV

        # Energy Window
        channel_name = f"{config.source.isotope}_channel_{i}"
        ewin = sim.add_actor("DigitizerEnergyWindowsActor", f"EnergyWin_{i}")
        ewin.attached_to = crystal.name
        ewin.input_digi_collection = blur.name
        ewin.channels = [
            {
                "name": channel_name,
                "min": digi_cfg.energy_window_min * keV,
                "max": digi_cfg.energy_window_max * keV,
            }
        ]

        # Projection
        proj = sim.add_actor("DigitizerProjectionActor", f"Projection_{i}")
        proj.attached_to = crystal.name
        proj.input_digi_collections = [channel_name]
        proj.size = list(digi_cfg.projection_size)
        proj.spacing = [
            digi_cfg.projection_spacing[0] * mm,
            digi_cfg.projection_spacing[1] * mm,
        ]
        proj.output_filename = f"{config.output_dir}/projection_{i}.mhd"

    print(f"✅ Added digitizer chain for {len(crystals)} heads")


# ==============================================================================
# Complete Simulation Setup
# ==============================================================================

def create_simulation(config: SPECTConfig, visu: bool = False, visu_type: str = "vrml"):
    """
    Create complete SPECT simulation from configuration

    Parameters:
    -----------
    config : SPECTConfig
        System configuration
    visu : bool
        Enable visualization
    visu_type : str
        Visualization type ("vrml" or "qt")

    Returns:
    --------
    gate.Simulation : Configured simulation object
    """
    cm = gate.g4_units.cm
    sec = gate.g4_units.second

    # Validate configuration
    if not config.validate():
        raise ValueError("Invalid configuration")

    print("\n" + "=" * 70)
    print("Creating GAGG SPECT Simulation")
    print("=" * 70)

    # Create simulation
    sim = gate.Simulation()

    # Materials
    add_materials(sim, config)
    sim.check_volumes_overlap = True

    # World
    world_size = max(200 * cm, config.fov.detector_radius * 3 * cm)
    sim.world.size = [world_size, world_size, world_size]
    sim.world.material = "Air"
    sim.world.visible = False

    # Geometry
    heads, crystals = add_detector_heads(sim, config)
    fov = add_fov_phantom(sim, config)

    # Source
    source = add_source(sim, config)

    # Digitizer
    add_digitizer(sim, config, crystals)

    # Physics
    sim.physics_manager.physics_list_name = config.physics_list
    sim.physics_manager.set_production_cut("world", "all", 1.0 * gate.g4_units.mm)
    sim.physics_manager.set_production_cut(
        crystals[0].name, "all", 0.1 * gate.g4_units.mm
    )

    # Timing
    sim.run_timing_intervals = [[0, config.acquisition.duration * sec]]

    # Detector rotation (if enabled)
    if config.acquisition.rotation_enabled:
        # Add rotation to first head (others follow via ring repeater)
        # Note: This simplified approach rotates all heads together
        # For more complex rotation, implement orbital movement
        print(f"⚠️  Rotation enabled but not yet implemented in this version")
        print(f"   Consider using GATE macro files for detector rotation")

    # Visualization
    sim.visu = visu
    sim.visu_type = visu_type

    print("\n" + "=" * 70)
    print("✅ Simulation created successfully!")
    print("=" * 70 + "\n")

    return sim


# ==============================================================================
# Main Entry Point
# ==============================================================================

if __name__ == "__main__":
    import click

    @click.command()
    @click.option(
        "--config",
        type=click.Path(exists=True),
        help="Path to JSON configuration file",
    )
    @click.option(
        "--preset",
        type=click.Choice(["small_animal", "clinical"]),
        default="small_animal",
        help="Use preset configuration",
    )
    @click.option("--visu", is_flag=True, help="Enable visualization")
    @click.option(
        "--visu-type",
        type=click.Choice(["vrml", "qt"]),
        default="vrml",
        help="Visualization type",
    )
    def main(config, preset, visu, visu_type):
        """Run GAGG SPECT simulation with configurable parameters"""

        # Load configuration
        if config:
            # Load from JSON file
            spect_config = SPECTConfig.from_json(config)
            print(f"✅ Loaded configuration from: {config}")
        else:
            # Use preset
            if preset == "small_animal":
                spect_config = SPECTConfig.default_small_animal()
            else:
                spect_config = SPECTConfig.default_clinical()
            print(f"✅ Using preset configuration: {preset}")

        # Print configuration summary
        spect_config.print_summary()

        # Create and run simulation
        sim = create_simulation(spect_config, visu=visu, visu_type=visu_type)
        sim.run()

        print("\n✅ Simulation completed!")

    main()
