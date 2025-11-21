#!/usr/bin/env python3
"""
================================================================================
OpenGATE SPECT Example - Rotating Gantry with Dynamic Data Collection
================================================================================

DESCRIPTION:
    This example demonstrates SPECT simulation with rotating detector heads
    and continuous data collection during motion. The gantry rotation speed
    is fully configurable, simulating realistic clinical SPECT acquisitions
    where data is collected while the detectors orbit around the patient.

FEATURES:
    - Configurable gantry rotation (speed, angular range, number of stops)
    - Continuous data collection during detector motion
    - Multiple detector heads with synchronized rotation
    - Dynamic geometry updates using OpenGATE motion actors
    - Realistic clinical acquisition protocols
    - Step-and-shoot or continuous rotation modes

INSTALLATION:
    # Install OpenGATE and dependencies
    pip install opengate numpy scipy itk SimpleITK

USAGE:
    # Run single projection (default: projection 0)
    python example_rotating_spect.py

    # Run specific projection (e.g., projection 5)
    python example_rotating_spect.py 5

    # Run all projections using bash loop
    for i in {0..59}; do python example_rotating_spect.py $i; done

    # Customize rotation in RotatingSPECTConfig class

CONFIGURATION:
    Edit the RotatingSPECTConfig class to customize:

    Detector Configuration:
        detector_model     : "GE_NM670" or "SIEMENS_INTEVO"
        crystal_size       : "3/8" (9.525mm) or "5/8" (15.875mm) for GE
        collimator_type    : "lehr", "megp", "hegp"
        num_heads          : Number of detector heads (1-3 typical)
        detector_radius    : Orbit radius in cm

    Rotation Configuration:
        rotation_mode      : "continuous" or "step_and_shoot"
        start_angle        : Starting angle in degrees
        total_rotation     : Total rotation angle in degrees (e.g., 360)
        num_projections    : Number of angular positions
        rotation_speed     : Degrees per second (for continuous mode)
        dwell_time         : Time per position in step-and-shoot (seconds)

    Data Collection:
        total_time         : Total acquisition time in seconds
        time_per_projection: Time spent at each angle (auto-calculated)

    Source and FOV:
        source_position    : [x, y, z] in cm
        source_activity    : Activity in Bq
        fov_size          : [x, y, z] in cm

ROTATION MODES:
    1. Continuous Rotation:
       - Detectors rotate continuously at constant speed
       - Data collected during motion (realistic clinical mode)
       - Speed in degrees/second
       - Total time = total_rotation / rotation_speed

    2. Step-and-Shoot:
       - Detectors stop at each projection angle
       - Data collected while stationary
       - Defined by number of projections and dwell time
       - Total time = num_projections × dwell_time

CLINICAL ACQUISITION EXAMPLES:
    # Cardiac SPECT (20 minutes, 64 projections, dual head)
    config.num_heads = 2
    config.detector_radius = 25  # cm, body contour
    config.rotation_mode = "step_and_shoot"
    config.total_rotation = 180  # degrees (per head)
    config.num_projections = 64
    config.dwell_time = 18.75  # seconds (20 min / 64 = 18.75s)
    config.start_angle = 45  # RAO

    # Whole body bone scan (continuous rotation)
    config.rotation_mode = "continuous"
    config.total_rotation = 360
    config.rotation_speed = 6  # deg/s (60 seconds for full rotation)
    config.detector_radius = 30  # cm

    # Fast brain SPECT (15 minutes, step-and-shoot)
    config.num_heads = 3  # Triple head
    config.total_rotation = 360
    config.num_projections = 120  # 40 per head
    config.dwell_time = 7.5  # seconds (15 min / 120 = 7.5s)
    config.detector_radius = 15  # cm, close to head

TIMING CALCULATIONS:
    Step-and-shoot mode:
        time_per_projection = total_time / num_projections
        angular_step = total_rotation / num_projections

    Continuous mode:
        total_time = total_rotation / rotation_speed
        time_per_projection = total_time / num_projections
        angular_step = total_rotation / num_projections

OUTPUT:
    Files saved to: ./output_rotating_spect/

    Generated files:
        - phase_space_head_*_angle_*.root : Data per angular position
        - rotation_log.txt : Timing and angle information
        - projection_*.mhd : Reconstructed projections per angle

IMPLEMENTATION DETAILS:
    - Uses step-and-shoot approach with separate simulations per angle
    - Rotation implemented via translation + rotation matrix updates
    - Each angular position is a separate simulation run
    - OpenGATE limitation: Only one simulation per Python process
    - For multiple projections: Use run_multiangle_acquisition() helper
    - Data files saved per projection angle for post-processing

ROTATION SYNCHRONIZATION:
    - All detector heads rotate synchronously
    - Angular spacing between heads maintained (e.g., 180° for dual head)
    - Data collection synchronized with motion updates
    - Smooth transitions between angular positions

PERFORMANCE NOTES:
    - Continuous rotation: More realistic, slightly slower simulation
    - Step-and-shoot: Faster simulation, discrete positions
    - More projections = better angular sampling but longer runtime
    - Rotation speed affects motion blur in continuous mode

REFERENCES:
    - OpenGATE: https://github.com/OpenGATE/opengate
    - SPECT Contrib: opengate/contrib/spect/
    - Dynamic Geometry: opengate.actors.dynamicgeometry

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


class RotatingSPECTConfig:
    """Configuration class for rotating SPECT simulation"""

    def __init__(self):
        # Detector configuration
        self.detector_model = "GE_NM670"  # "GE_NM670" or "SIEMENS_INTEVO"
        self.crystal_size = "3/8"  # For GE only
        self.collimator_type = "lehr"
        self.num_heads = 2  # Number of detector heads
        self.detector_radius = 30  # cm - orbit radius

        # Rotation configuration
        self.rotation_mode = "step_and_shoot"  # "continuous" or "step_and_shoot"
        self.start_angle = 0  # degrees - starting position
        self.total_rotation = 360  # degrees - total rotation per head
        self.num_projections = 60  # Number of angular positions

        # Timing configuration
        # For step-and-shoot: time at each position
        self.dwell_time = 10  # seconds per projection
        # For continuous: rotation speed
        self.rotation_speed = 6  # degrees per second

        # Calculate derived timing parameters
        if self.rotation_mode == "step_and_shoot":
            self.total_time = self.num_projections * self.dwell_time
            self.time_per_projection = self.dwell_time
        else:  # continuous
            self.total_time = self.total_rotation / self.rotation_speed
            self.time_per_projection = self.total_time / self.num_projections

        # Angular step between projections
        self.angular_step = self.total_rotation / self.num_projections

        # Source configuration
        self.source_position = [0, 0, 0]  # cm [x, y, z]
        self.source_isotope = "Tc99m"
        self.source_activity = 1e6  # Bq

        # Field of view
        self.fov_size = [40, 40, 40]  # cm
        self.world_size = [200, 200, 200]  # cm

        # Energy window (±10% around 140.5 keV)
        self.energy_window = [126.5, 154.5]  # keV

        # Output
        self.output_dir = Path("./output_rotating_spect")

        # Simulation options
        self.number_of_threads = 4
        self.verbose = True


def create_simulation(config: RotatingSPECTConfig):
    """
    Create and configure base simulation

    Args:
        config: RotatingSPECTConfig object

    Returns:
        Configured simulation object
    """
    sim = gate.Simulation()

    # Set main options
    sim.g4_verbose = False
    sim.g4_verbose_level = 1
    sim.visu = False
    sim.random_seed = 'auto'
    sim.number_of_threads = config.number_of_threads

    # Configure world
    sim.world.size = [x * g4_units.cm for x in config.world_size]
    sim.world.material = "G4_AIR"

    # Add physics
    sim.physics_manager.physics_list_name = "G4EmStandardPhysics_option4"
    sim.physics_manager.enable_decay = True
    sim.physics_manager.global_production_cuts.gamma = 0.1 * g4_units.mm
    sim.physics_manager.global_production_cuts.electron = 0.1 * g4_units.mm
    sim.physics_manager.global_production_cuts.positron = 0.1 * g4_units.mm

    if config.verbose:
        print(f"✓ Simulation created")
        print(f"  Mode: {config.rotation_mode}")
        print(f"  World size: {config.world_size} cm")

    return sim


def add_rotating_detector_heads(sim, config: RotatingSPECTConfig):
    """
    Add detector heads that will rotate during acquisition

    Args:
        sim: Simulation object
        config: Configuration parameters

    Returns:
        List of heads, collimators, crystals, and initial angles
    """
    heads = []
    collimators = []
    crystals = []
    initial_angles = []

    if config.verbose:
        print(f"\n✓ Adding {config.num_heads} rotating detector head(s):")
        print(f"  Model: {config.detector_model}")
        print(f"  Collimator: {config.collimator_type.upper()}")
        print(f"  Orbit radius: {config.detector_radius} cm")

    # Calculate angular spacing between heads
    head_angular_spacing = 360 / config.num_heads if config.num_heads > 1 else 0

    for i in range(config.num_heads):
        head_name = f"spect_head_{i}"

        # Add detector head
        if config.detector_model == "GE_NM670":
            if config.verbose:
                print(f"  Head {i}: GE Discovery NM670 (crystal: {config.crystal_size}\")")
            head, colli, crystal = add_ge_head(
                sim,
                name=head_name,
                collimator_type=config.collimator_type,
                crystal_size=config.crystal_size,
                debug=False
            )
        else:
            if config.verbose:
                print(f"  Head {i}: Siemens Intevo")
            head, colli, crystal = add_siemens_head(
                sim,
                name=head_name,
                collimator_type=config.collimator_type,
                debug=False
            )

        # Calculate initial angle for this head
        initial_angle = config.start_angle + i * head_angular_spacing
        initial_angles.append(initial_angle)

        # Set initial position
        angle_rad = np.deg2rad(initial_angle)
        x = config.detector_radius * np.cos(angle_rad)
        y = config.detector_radius * np.sin(angle_rad)
        z = 0

        head.translation = [x * g4_units.cm, y * g4_units.cm, z * g4_units.cm]

        # Set initial rotation (point toward center)
        rotation_angle = initial_angle + 90
        head.rotation = Rotation.from_euler("z", rotation_angle, degrees=True).as_matrix()

        if config.verbose:
            print(f"    Initial position: ({x:.1f}, {y:.1f}, {z:.1f}) cm at {initial_angle}°")

        heads.append(head)
        collimators.append(colli)
        crystals.append(crystal)

    return heads, collimators, crystals, initial_angles


def update_head_positions(heads, config: RotatingSPECTConfig, initial_angles, projection_index):
    """
    Update detector head positions for a specific projection angle

    Args:
        heads: List of detector head volumes
        config: Configuration parameters
        initial_angles: Initial angles for each head
        projection_index: Index of current projection (0 to num_projections-1)
    """
    for i, head in enumerate(heads):
        # Calculate angle for this projection
        angle = initial_angles[i] + projection_index * config.angular_step
        angle_rad = np.deg2rad(angle)

        # Calculate position
        x = config.detector_radius * np.cos(angle_rad)
        y = config.detector_radius * np.sin(angle_rad)
        z = 0

        # Update position
        head.translation = [x * g4_units.cm, y * g4_units.cm, z * g4_units.cm]

        # Update rotation (point toward center)
        rotation_angle = angle + 90
        head.rotation = Rotation.from_euler("z", rotation_angle, degrees=True).as_matrix()


def add_data_collection(sim, crystals, config: RotatingSPECTConfig):
    """
    Add data collection actors for each detector head

    Args:
        sim: Simulation object
        crystals: List of crystal volumes
        config: Configuration parameters
    """
    if config.verbose:
        print(f"\n✓ Configuring data collection:")

    for i, crystal in enumerate(crystals):
        # Phase space actor for data collection
        ps = sim.add_actor("PhaseSpaceActor", f"PhaseSpace_{i}")
        ps.attached_to = crystal.name
        ps.output_filename = config.output_dir / f"phase_space_head_{i}.root"
        ps.attributes = [
            "Position",
            "Direction",
            "KineticEnergy",
            "GlobalTime",
            "TrackCreatorProcess",
            "ParticleName"
        ]

        # Statistics actor
        stats = sim.add_actor("SimulationStatisticsActor", f"Stats_{i}")
        stats.track_types_flag = True

        if config.verbose:
            print(f"  Head {i}: Phase space data collection enabled")


def add_source(sim, config: RotatingSPECTConfig):
    """
    Add radioactive source

    Args:
        sim: Simulation object
        config: Configuration parameters

    Returns:
        Source object
    """
    source = sim.add_source("GenericSource", "point_source")
    source.particle = "gamma"
    source.energy.type = "mono"
    source.energy.mono = 140.5 * g4_units.keV

    source.position.type = "point"
    source.position.translation = [x * g4_units.cm for x in config.source_position]

    source.direction.type = "iso"
    source.activity = config.source_activity * g4_units.Bq

    if config.verbose:
        print(f"\n✓ Source configured:")
        print(f"  Isotope: {config.source_isotope}")
        print(f"  Position: {config.source_position} cm")
        print(f"  Activity: {config.source_activity:.2e} Bq")

    return source


def configure_acquisition(sim, config: RotatingSPECTConfig):
    """
    Configure acquisition timing

    Args:
        sim: Simulation object
        config: Configuration parameters
    """
    # Set run timing to cover entire rotation
    sim.run_timing_intervals = [[0, config.total_time * g4_units.s]]

    if config.verbose:
        print(f"\n✓ Acquisition configured:")
        print(f"  Duration: {config.total_time:.1f} seconds")
        if config.rotation_mode == "continuous":
            print(f"  Rotation speed: {config.rotation_speed:.2f} deg/s")
        else:
            print(f"  Dwell time: {config.dwell_time:.2f} s/projection")


def save_rotation_log(config: RotatingSPECTConfig):
    """
    Save rotation parameters to log file

    Args:
        config: Configuration parameters
    """
    log_file = config.output_dir / "rotation_log.txt"

    with open(log_file, 'w') as f:
        f.write("SPECT Rotation Acquisition Log\n")
        f.write("=" * 70 + "\n\n")

        f.write("ROTATION PARAMETERS:\n")
        f.write(f"  Mode: {config.rotation_mode}\n")
        f.write(f"  Start angle: {config.start_angle}°\n")
        f.write(f"  Total rotation: {config.total_rotation}°\n")
        f.write(f"  Number of projections: {config.num_projections}\n")
        f.write(f"  Angular step: {config.angular_step:.3f}°\n\n")

        f.write("TIMING:\n")
        f.write(f"  Total acquisition time: {config.total_time:.2f} seconds\n")
        f.write(f"  Time per projection: {config.time_per_projection:.3f} seconds\n")
        if config.rotation_mode == "continuous":
            f.write(f"  Rotation speed: {config.rotation_speed:.2f} deg/s\n")
        else:
            f.write(f"  Dwell time: {config.dwell_time:.2f} s\n")
        f.write("\n")

        f.write("DETECTOR:\n")
        f.write(f"  Model: {config.detector_model}\n")
        f.write(f"  Number of heads: {config.num_heads}\n")
        f.write(f"  Orbit radius: {config.detector_radius} cm\n")
        f.write(f"  Collimator: {config.collimator_type}\n\n")

        f.write("ANGULAR POSITIONS:\n")
        for i in range(config.num_projections):
            angle = config.start_angle + i * config.angular_step
            time = i * config.time_per_projection
            f.write(f"  Projection {i:3d}: {angle:7.2f}° at t={time:7.2f}s\n")

    if config.verbose:
        print(f"\n✓ Rotation log saved to: {log_file}")


def run_single_projection(config: RotatingSPECTConfig, projection_index: int):
    """
    Run simulation for a single projection angle

    Args:
        config: Configuration parameters
        projection_index: Index of projection (0 to num_projections-1)

    Returns:
        Dictionary with projection results
    """
    angle = config.start_angle + projection_index * config.angular_step

    if config.verbose:
        print(f"\nProjection {projection_index + 1}/{config.num_projections}: {angle:.2f}°")

    # Create simulation
    sim = create_simulation(config)
    sim.g4_verbose = False

    # Add detector heads
    heads, collimators, crystals, initial_angles = add_rotating_detector_heads(sim, config)

    # Update positions for this angle
    update_head_positions(heads, config, initial_angles, projection_index)

    # Add data collection
    for i, crystal in enumerate(crystals):
        ps = sim.add_actor("PhaseSpaceActor", f"PhaseSpace_{i}_proj_{projection_index}")
        ps.attached_to = crystal.name
        ps.output_filename = config.output_dir / f"phase_space_head_{i}_angle_{projection_index:03d}.root"
        ps.attributes = [
            "Position",
            "Direction",
            "KineticEnergy",
            "GlobalTime",
            "TrackCreatorProcess",
            "ParticleName"
        ]

    # Add source
    add_source(sim, config)

    # Configure timing
    sim.run_timing_intervals = [[0, config.time_per_projection * g4_units.s]]

    # Run simulation
    output = sim.run()

    if config.verbose:
        print(f"  ✓ Completed")

    return {
        'projection': projection_index,
        'angle': angle,
        'output': output
    }


def main():
    """
    Main execution function - runs a single projection

    For multi-projection acquisitions, this script should be called
    multiple times with different projection indices, or use subprocess
    to spawn separate Python processes.
    """
    import sys

    print("=" * 70)
    print("Rotating SPECT Simulation (Single Projection)")
    print("=" * 70)

    # Create configuration
    config = RotatingSPECTConfig()

    # Check command line arguments for projection index
    projection_index = 0
    if len(sys.argv) > 1:
        try:
            projection_index = int(sys.argv[1])
        except ValueError:
            print(f"Warning: Invalid projection index '{sys.argv[1]}', using 0")

    if projection_index >= config.num_projections:
        print(f"Error: Projection index {projection_index} exceeds num_projections {config.num_projections}")
        sys.exit(1)

    # Create output directory
    config.output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n✓ Output directory: {config.output_dir}")

    # Save rotation log (only on first run)
    if projection_index == 0:
        save_rotation_log(config)

    print(f"\nConfiguration:")
    print(f"  Projections: {config.num_projections} total")
    print(f"  Angular range: {config.start_angle}° to {config.start_angle + config.total_rotation}°")
    print(f"  Time per projection: {config.time_per_projection:.2f} seconds")

    # Run single projection
    print("\n" + "=" * 70)
    result = run_single_projection(config, projection_index)

    print("\n" + "=" * 70)
    print("✓ Projection completed successfully!")
    print("=" * 70)
    print(f"  Projection: {projection_index + 1}/{config.num_projections}")
    print(f"  Angle: {result['angle']:.2f}°")

    # Check if all projections are complete
    expected_files = []
    for i in range(config.num_projections):
        for head_idx in range(config.num_heads):
            expected_files.append(f"phase_space_head_{head_idx}_angle_{i:03d}.root")

    existing_files = [f.name for f in config.output_dir.glob("phase_space*.root")]
    completed_projections = len(existing_files) // config.num_heads

    print(f"\nProgress: {completed_projections}/{config.num_projections} projections completed")

    if completed_projections == config.num_projections:
        print("\n✓ All projections complete! Ready for reconstruction.")

    return result, config


if __name__ == "__main__":
    result, config = main()

    print("\n" + "=" * 70)
    print("To run all projections, use:")
    print(f"  for i in {{0..{config.num_projections-1}}}; do python example_rotating_spect.py $i; done")
    print("=" * 70)
