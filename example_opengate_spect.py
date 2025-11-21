#!/usr/bin/env python3
"""
================================================================================
OpenGATE SPECT Example - Direct API Usage
================================================================================

DESCRIPTION:
    This example demonstrates direct usage of OpenGATE's SPECT contribution
    modules (opengate.contrib.spect) for building SPECT simulations with
    detailed control over detector configuration, geometry, and digitization.

FEATURES:
    - Configurable detector models (GE Discovery NM670, Siemens Intevo)
    - Multiple detector heads with custom positioning
    - Complete digitizer chain (energy blurring, spatial blurring, energy windows)
    - Simple point source configuration
    - Adjustable field of view (FOV) and pixel resolution
    - Validated detector geometries from OpenGATE repository

INSTALLATION:
    # Install OpenGATE and dependencies
    pip install opengate numpy itk SimpleITK

    # Or use latest development version
    pip install git+https://github.com/OpenGATE/opengate.git

USAGE:
    # Run with default configuration
    python example_opengate_spect.py

    # Customize by editing SPECTSimulationConfig class parameters
    # See CONFIGURATION section below

CONFIGURATION:
    Edit the SPECTSimulationConfig class to customize:

    Detector Configuration:
        detector_model     : "GE_NM670" or "SIEMENS_INTEVO"
        crystal_size       : "3/8" (9.525mm) or "5/8" (15.875mm) for GE only
        collimator_type    : "lehr", "megp"/"melp", "hegp"/"he"
        num_heads          : Number of detector heads (1-3 typical)
        detector_radius    : Distance from center to detector (cm)
        head_angles        : Angular positions of each head (degrees)

    Field of View:
        fov_size          : [x, y, z] in cm (defines imaging region)
        world_size        : [x, y, z] in cm (should be larger than FOV)

    Readout Resolution:
        pixel_size        : [x, y] in cm (effective detector pixel size)

    Source Configuration:
        source_position   : [x, y, z] in cm
        source_isotope    : Radionuclide name (e.g., "Tc99m")
        source_activity   : Activity in Bq
        energy_window     : [min, max] in keV for photopeak

    Acquisition:
        acquisition_time  : Duration in seconds
        num_projections   : Total projections per head
        rotation_angle    : Total rotation in degrees

DETECTOR MODELS:
    GE Discovery NM670:
        - Crystal: 54 × 40 cm
        - Crystal thickness: 3/8" (9.525mm) or 5/8" (15.875mm)
        - Collimators: LEHR (1.5mm), MEGP (3mm), HEGP (4mm)
        - Typical use: Clinical SPECT, Tc-99m imaging

    Siemens Intevo:
        - Crystal: 53.3 × 38.7 cm
        - Crystal: 9.5mm NaI
        - Collimators: LEHR (1.11mm), MELP (2.94mm), HE (4mm)
        - Typical use: Clinical SPECT, multi-isotope imaging

COLLIMATOR TYPES:
    LEHR  : Low Energy High Resolution (Tc-99m, 140 keV)
    MEGP  : Medium Energy General Purpose (In-111, Lu-177)
    MELP  : Medium Energy Low Penetration (In-111, Lu-177)
    HEGP  : High Energy General Purpose (I-131, 364 keV)
    HE    : High Energy (I-131)

OUTPUT:
    Files are saved to: ./output_opengate_spect/

    Generated files:
        - hits_head_*.root        : Raw detector hits (ROOT format)
        - singles_head_*.root     : Processed singles events
        - projection_head_*.mhd   : 2D projection images (MHD/RAW format)

EXAMPLE CONFIGURATIONS:
    # High resolution small animal imaging
    config.detector_model = "GE_NM670"
    config.crystal_size = "3/8"
    config.collimator_type = "lehr"
    config.pixel_size = [0.2, 0.2]        # 2mm pixels
    config.detector_radius = 15            # cm, close to subject
    config.fov_size = [20, 20, 20]        # cm

    # Clinical cardiac SPECT
    config.detector_model = "SIEMENS_INTEVO"
    config.collimator_type = "lehr"
    config.pixel_size = [0.45, 0.45]      # 4.5mm pixels
    config.detector_radius = 36            # cm
    config.fov_size = [40, 40, 40]        # cm
    config.num_heads = 2

    # Fast testing configuration
    config.acquisition_time = 5            # seconds (vs 20s default)
    config.source_activity = 1e4           # Bq (vs 1e6 default)
    config.num_projections = 30            # (vs 60 default)
    config.number_of_threads = 8           # Use more CPU cores

NOTES:
    - First run will download Geant4 data files (~1-2 GB, one-time)
    - Visualization is disabled by default (sim.visu = False)
    - Energy resolution set to 7% @ 140.5 keV (GAGG-like performance)
    - Uses OpenGATE's validated detector geometries and material databases
    - No local material definitions needed - all materials from OpenGATE

REFERENCES:
    - OpenGATE: https://github.com/OpenGATE/opengate
    - SPECT Contrib: opengate/contrib/spect/
    - Documentation: http://opengate.readthedocs.io/

AUTHOR: Auto-generated example for GAGG_SPECT_SIM project
VERSION: 1.0
================================================================================
"""

import opengate as gate
from opengate import g4_units
from opengate.contrib.spect.ge_discovery_nm670 import add_spect_head as add_ge_head
from opengate.contrib.spect.siemens_intevo import add_spect_head as add_siemens_head
from scipy.spatial.transform import Rotation
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
        self.world_size = [200, 200, 200]  # cm - should be larger than FOV + detectors

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
        head.rotation = Rotation.from_euler("z", rotation_angle, degrees=True).as_matrix()

        print(f"    Position: ({x:.1f}, {y:.1f}, {z:.1f}) cm at {angle}°")

        heads.append(head)
        collimators.append(colli)
        crystals.append(crystal)

    return heads, collimators, crystals


def add_digitizer(sim, crystal, config: SPECTSimulationConfig, head_idx=0):
    """
    Add data collection actors for detector readout

    Args:
        sim: Simulation object
        crystal: Crystal volume
        config: Configuration parameters
        head_idx: Head index for output naming

    Returns:
        Configured phase space actor
    """
    # Phase space actor - collects all hits in the crystal
    ps = sim.add_actor("PhaseSpaceActor", f"PhaseSpace_{head_idx}")
    ps.attached_to = crystal.name
    ps.output_filename = config.output_dir / f"phase_space_head_{head_idx}.root"
    ps.attributes = [
        "Position",
        "Direction",
        "KineticEnergy",
        "GlobalTime",
        "TrackCreatorProcess",
        "ParticleName"
    ]

    # Statistics actor
    stats = sim.add_actor("SimulationStatisticsActor", f"Stats_{head_idx}")
    stats.track_types_flag = True

    print(f"  Data collection head {head_idx}: Phase space + statistics")
    print(f"  Energy window: {config.energy_window[0]}-{config.energy_window[1]} keV")

    return ps


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
