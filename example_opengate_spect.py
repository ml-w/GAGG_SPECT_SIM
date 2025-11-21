#!/usr/bin/env python3
"""
Example demonstrating OpenGATE SPECT Contribution Code Reuse

This script shows how to configure a SPECT simulation using the
opengate.contrib.spect module with configurable parameters:
- Field of View (FOV)
- Crystal type (GE NM670 or Siemens Intevo)
- SPECT head dimensions and readout resolution
- Simple point source

Installation:
    pip install opengate

Usage:
    python example_opengate_spect.py
"""

import opengate as gate
from opengate import g4_units
from opengate.contrib.spect.ge_discovery_nm670 import add_spect_head as add_ge_head
from opengate.contrib.spect.siemens_intevo import add_spect_head as add_siemens_head
from pathlib import Path
import numpy as np


class SPECTSimulationConfig:
    """Configuration class for SPECT simulation parameters"""

    def __init__(self):
        # System configuration
        self.detector_model = "GE_NM670"  # Options: "GE_NM670", "SIEMENS_INTEVO"
        self.crystal_size = "3/8"  # For GE: "3/8" (9.525mm) or "5/8" (15.875mm)
        self.collimator_type = "lehr"  # Options: "lehr", "megp"/"melp", "hegp"/"he"

        # Field of View (FOV) configuration
        self.fov_size = [40, 40, 40]  # cm [x, y, z]
        self.world_size = [100, 100, 100]  # cm - should be larger than FOV

        # SPECT head configuration
        self.num_heads = 2  # Number of detector heads
        self.detector_radius = 36  # cm - distance from center to detector
        self.head_angles = [0, 180]  # degrees - positioning of each head

        # Readout resolution (detector pixel size)
        self.pixel_size = [0.35, 0.35]  # cm [x, y] - effective pixel size

        # Acquisition parameters
        self.num_projections = 60  # Total projections per head
        self.rotation_angle = 360  # degrees - total rotation
        self.acquisition_time = 20  # seconds

        # Source configuration (simple point source)
        self.source_position = [0, 0, 0]  # cm [x, y, z]
        self.source_isotope = "Tc99m"
        self.source_activity = 1e6  # Bq

        # Energy window
        self.energy_window = [126.5, 154.5]  # keV - ±10% around 140.5 keV

        # Output configuration
        self.output_dir = Path("./output_opengate_spect")


def create_simulation(config: SPECTSimulationConfig):
    """
    Create and configure SPECT simulation using OpenGATE contrib

    Args:
        config: SPECTSimulationConfig object with simulation parameters

    Returns:
        Configured simulation object
    """
    # Initialize simulation
    sim = gate.Simulation()

    # Set main options
    sim.g4_verbose = False
    sim.g4_verbose_level = 1
    sim.visu = False
    sim.random_seed = 'auto'
    sim.number_of_threads = 4

    # Configure world
    sim.world.size = [x * g4_units.cm for x in config.world_size]
    sim.world.material = "G4_AIR"

    # Add physics list
    sim.physics_manager.physics_list_name = "G4EmStandardPhysics_option4"
    sim.physics_manager.enable_decay = True
    sim.physics_manager.global_production_cuts.gamma = 0.1 * g4_units.mm
    sim.physics_manager.global_production_cuts.electron = 0.1 * g4_units.mm
    sim.physics_manager.global_production_cuts.positron = 0.1 * g4_units.mm

    print(f"✓ World and physics configured")
    print(f"  World size: {config.world_size} cm")
    print(f"  FOV size: {config.fov_size} cm")

    return sim


def add_detector_heads(sim, config: SPECTSimulationConfig):
    """
    Add SPECT detector heads using OpenGATE contrib modules

    Args:
        sim: Simulation object
        config: Configuration parameters

    Returns:
        List of detector heads, collimators, and crystals
    """
    heads = []
    collimators = []
    crystals = []

    print(f"\n✓ Adding {config.num_heads} detector head(s):")
    print(f"  Model: {config.detector_model}")
    print(f"  Collimator: {config.collimator_type.upper()}")

    for i in range(config.num_heads):
        head_name = f"spect_head_{i}"

        # Select detector model
        if config.detector_model == "GE_NM670":
            print(f"  Head {i}: GE Discovery NM670 (crystal: {config.crystal_size}\")")
            head, colli, crystal = add_ge_head(
                sim,
                name=head_name,
                collimator_type=config.collimator_type,
                crystal_size=config.crystal_size,
                debug=False
            )
        elif config.detector_model == "SIEMENS_INTEVO":
            print(f"  Head {i}: Siemens Intevo")
            head, colli, crystal = add_siemens_head(
                sim,
                name=head_name,
                collimator_type=config.collimator_type,
                debug=False
            )
        else:
            raise ValueError(f"Unknown detector model: {config.detector_model}")

        # Position the head
        angle = config.head_angles[i] if i < len(config.head_angles) else i * (360 / config.num_heads)
        angle_rad = np.deg2rad(angle)

        # Calculate position (heads point toward center)
        x = config.detector_radius * np.cos(angle_rad)
        y = config.detector_radius * np.sin(angle_rad)
        z = 0

        head.translation = [x * g4_units.cm, y * g4_units.cm, z * g4_units.cm]

        # Rotate head to point toward center
        rotation_angle = angle + 90  # Point toward center
        head.rotation = gate.Rotation.from_euler("z", rotation_angle, degrees=True)

        print(f"    Position: ({x:.1f}, {y:.1f}, {z:.1f}) cm at {angle}°")

        heads.append(head)
        collimators.append(colli)
        crystals.append(crystal)

    return heads, collimators, crystals


def add_digitizer(sim, crystal, config: SPECTSimulationConfig, head_idx=0):
    """
    Add digitizer chain for detector readout

    Args:
        sim: Simulation object
        crystal: Crystal volume
        config: Configuration parameters
        head_idx: Head index for output naming

    Returns:
        Configured projection actor
    """
    # Hits collection
    hc = sim.add_actor("DigitizerHitsCollectionActor", f"Hits_{head_idx}")
    hc.attached_to = crystal.name
    hc.output_filename = config.output_dir / f"hits_head_{head_idx}.root"
    hc.attributes = [
        "PostPosition",
        "TotalEnergyDeposit",
        "GlobalTime",
        "TrackVolumeName"
    ]

    # Singles collection
    sc = sim.add_actor("DigitizerAdderActor", f"Singles_{head_idx}")
    sc.attached_to = hc.name
    sc.policy = "EnergyWinnerPosition"
    sc.output_filename = config.output_dir / f"singles_head_{head_idx}.root"

    # Energy blurring (7% resolution @ 140.5 keV for GAGG-like performance)
    eb = sim.add_actor("DigitizerEnergyBlurringActor", f"EnergyBlur_{head_idx}")
    eb.attached_to = sc.name
    eb.blur_attribute = "TotalEnergyDeposit"
    eb.blur_method = "Gaussian"
    eb.blur_fwhm = 0.07  # 7% resolution
    eb.blur_reference_value = 140.5 * g4_units.keV

    # Spatial blurring based on pixel size
    sb = sim.add_actor("DigitizerSpatialBlurringActor", f"SpatialBlur_{head_idx}")
    sb.attached_to = eb.name
    sb.blur_attribute = "PostPosition"
    sb.blur_fwhm = config.pixel_size[0] * g4_units.cm

    # Energy window
    ew = sim.add_actor("DigitizerEnergyWindowsActor", f"EnergyWindow_{head_idx}")
    ew.attached_to = sb.name
    ew.channels = [
        {
            "name": "photopeak",
            "min": config.energy_window[0] * g4_units.keV,
            "max": config.energy_window[1] * g4_units.keV,
        }
    ]

    # Projection actor
    proj = sim.add_actor("DigitizerProjectionActor", f"Projection_{head_idx}")
    proj.attached_to = ew.name
    proj.output_filename = config.output_dir / f"projection_head_{head_idx}.mhd"

    # Set projection size based on detector and pixel size
    # For GE NM670: crystal is 54 x 40 cm
    # For Siemens Intevo: crystal is ~53.3 x 38.7 cm
    if config.detector_model == "GE_NM670":
        detector_size = [54, 40]  # cm
    else:
        detector_size = [53.3, 38.7]  # cm

    proj.size = [
        int(detector_size[0] / config.pixel_size[0]),
        int(detector_size[1] / config.pixel_size[1])
    ]
    proj.spacing = [config.pixel_size[0] * g4_units.cm, config.pixel_size[1] * g4_units.cm]

    print(f"  Digitizer head {head_idx}: {proj.size[0]}×{proj.size[1]} pixels")
    print(f"  Pixel size: {config.pixel_size[0]:.2f} × {config.pixel_size[1]:.2f} cm")
    print(f"  Energy window: {config.energy_window[0]}-{config.energy_window[1]} keV")

    return proj


def add_simple_source(sim, config: SPECTSimulationConfig):
    """
    Add a simple point source

    Args:
        sim: Simulation object
        config: Configuration parameters

    Returns:
        Source object
    """
    source = sim.add_source("GenericSource", "point_source")
    source.particle = "gamma"
    source.energy.type = "mono"
    source.energy.mono = 140.5 * g4_units.keV  # Tc-99m photopeak

    source.position.type = "point"
    source.position.translation = [x * g4_units.cm for x in config.source_position]

    source.direction.type = "iso"

    source.activity = config.source_activity * g4_units.Bq

    print(f"\n✓ Source configured:")
    print(f"  Isotope: {config.source_isotope}")
    print(f"  Position: {config.source_position} cm")
    print(f"  Activity: {config.source_activity:.2e} Bq")
    print(f"  Energy: 140.5 keV (Tc-99m)")

    return source


def configure_acquisition(sim, config: SPECTSimulationConfig):
    """
    Configure acquisition timing

    Args:
        sim: Simulation object
        config: Configuration parameters
    """
    sim.run_timing_intervals = [[0, config.acquisition_time * g4_units.s]]

    print(f"\n✓ Acquisition configured:")
    print(f"  Duration: {config.acquisition_time} seconds")
    print(f"  Projections: {config.num_projections} per head")

    # Note: For rotating gantry, you would add rotation here
    # using the OpenGATE contrib rotate_gantry() function


def main():
    """Main execution function"""

    print("=" * 60)
    print("SPECT Simulation using OpenGATE Contribution Code")
    print("=" * 60)

    # Create configuration
    config = SPECTSimulationConfig()

    # Create output directory
    config.output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n✓ Output directory: {config.output_dir}")

    # Create simulation
    sim = create_simulation(config)

    # Add detector heads
    heads, collimators, crystals = add_detector_heads(sim, config)

    # Add digitizers for each head
    print(f"\n✓ Configuring digitizers:")
    for i, crystal in enumerate(crystals):
        add_digitizer(sim, crystal, config, head_idx=i)

    # Add source
    add_simple_source(sim, config)

    # Configure acquisition
    configure_acquisition(sim, config)

    # Run simulation
    print("\n" + "=" * 60)
    print("Starting simulation...")
    print("=" * 60)

    try:
        sim.run()

        # Print statistics
        print("\n" + "=" * 60)
        print("Simulation completed successfully!")
        print("=" * 60)

        stats = sim.get_actor_user_info("Singles_0")
        if stats:
            print(f"\nStatistics (Head 0):")
            print(f"  Events detected: {stats.counts.event_count}")

        print(f"\nOutput files saved to: {config.output_dir}")

    except Exception as e:
        print(f"\n❌ Simulation failed: {e}")
        raise

    return sim, config


if __name__ == "__main__":
    # Run the simulation
    sim, config = main()

    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)
    print("\nTo customize the simulation, modify the SPECTSimulationConfig class:")
    print("  - detector_model: 'GE_NM670' or 'SIEMENS_INTEVO'")
    print("  - crystal_size: '3/8' or '5/8' (for GE)")
    print("  - collimator_type: 'lehr', 'megp', 'hegp'")
    print("  - fov_size: Field of view dimensions")
    print("  - pixel_size: Detector readout resolution")
    print("  - source_position: Location of point source")
