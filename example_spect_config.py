#!/usr/bin/env python3
"""
================================================================================
OpenGATE SPECT Example - High-Level SPECTConfig API
================================================================================

DESCRIPTION:
    This example demonstrates the high-level SPECTConfig class from OpenGATE's
    SPECT contribution module for comprehensive SPECT simulation configuration.
    This approach is ideal for complex simulations with voxelized phantoms,
    activity distributions, and advanced acquisition protocols.

FEATURES:
    - High-level configuration through SPECTConfig class
    - Automatic sub-configuration instantiation (detector, phantom, source, acquisition)
    - Voxelized phantom support with HU to material conversion
    - Activity distribution from images or numpy arrays
    - JSON serialization for reproducibility
    - Gantry rotation and multi-angle acquisition
    - Support for GE NM670 and Siemens Intevo detectors

INSTALLATION:
    # Install OpenGATE and dependencies
    pip install opengate numpy itk SimpleITK

    # Or use latest development version
    pip install git+https://github.com/OpenGATE/opengate.git

USAGE:
    # Run full example
    python example_spect_config.py

    # The script includes three modes (change in main() function):
    #   "full"      : Complete simulation setup (default)
    #   "minimal"   : Simplest configuration for quick testing
    #   "serialize" : Demonstration of JSON save/load

CONFIGURATION:
    The SPECTConfig class has auto-created sub-configurations:

    1. Detector Configuration (config.detector_config):
        model                : "Intevo" or "NM670"
        collimator           : "lehr", "melp", "he" (Intevo) or "megp", "hegp" (NM670)
        crystal_size         : "3/8" or "5/8" (NM670 only)
        number_of_heads      : 1, 2, 3, etc.
        energy_resolution    : Fractional resolution (e.g., 0.07 = 7%)
        energy_reference     : Reference energy in keV (e.g., 140.5)
        energy_windows       : List of {"name", "min", "max"} dictionaries
        spatial_blur_fwhm    : Spatial blurring in cm (pixel size)

    2. Phantom Configuration (config.phantom_config):
        size                 : [nx, ny, nz] voxel dimensions
        voxel_size           : [dx, dy, dz] in cm
        image_path           : Path to phantom image file
        hu_to_material_mode  : "GateMaterials" or custom
        density_tolerance    : Tolerance in g/cm³
        translation          : [x, y, z] position in cm

    3. Source Configuration (config.source_config):
        isotope              : Radionuclide name (e.g., "Tc99m", "Lu177")
        total_activity       : Total activity in Bq
        activity_distribution: Numpy array with normalized distribution
        activity_voxel_size  : Voxel size for activity distribution
        activity_image_path  : Path to activity image file

    4. Acquisition Configuration (config.acquisition_config):
        radius               : Gantry radius in cm
        number_of_projections: Total number of projections
        start_angle_deg      : Starting angle in degrees
        angular_span         : Total rotation in degrees
        duration             : Acquisition time in seconds

    5. Main Configuration (config):
        number_of_threads    : Number of parallel threads
        random_seed          : Random seed for reproducibility
        visu                 : Enable/disable visualization
        verbose              : Enable/disable verbose output
        output_folder        : Path for output files

DETECTOR MODELS:
    Siemens Intevo:
        - Crystal: 53.3 × 38.7 cm, 9.5mm NaI
        - Collimators: lehr (1.11mm), melp (2.94mm), he (4mm)
        - Material database: spect_siemens_intevo_materials.db

    GE Discovery NM670:
        - Crystal: 54 × 40 cm
        - Crystal thickness: 3/8" (9.525mm) or 5/8" (15.875mm)
        - Collimators: lehr (1.5mm), megp (3mm), hegp (4mm)
        - Material database: spect_ge_nm670_materials.db

WORKFLOW:
    1. Create SPECTConfig instance (auto-creates sub-configs)
    2. Configure detector settings
    3. Configure acquisition parameters
    4. Configure phantom (FOV definition)
    5. Configure source (activity distribution)
    6. Set output directory
    7. Initialize simulation from config
    8. Run simulation

OUTPUT:
    Files are saved to: ./output_spect_config/

    Generated files:
        - Projection images (MHD/RAW format)
        - ROOT files with hits and singles
        - JSON configuration file (if serialized)

EXAMPLE USAGE:
    # Minimal configuration
    config = spect_config.SPECTConfig()
    config.detector_config.model = "Intevo"
    config.detector_config.collimator = "lehr"
    config.acquisition_config.radius = 30
    config.acquisition_config.duration = 10
    sim = config.initialize_simulation()
    sim.run()

    # Save/Load configuration
    config.to_json("my_config.json")
    loaded = spect_config.SPECTConfig.from_json("my_config.json")

    # Custom activity distribution
    activity = np.zeros((100, 100, 100))
    activity[40:60, 40:60, 45:55] = 1.0
    activity = activity / np.sum(activity)
    config.source_config.activity_distribution = activity

ADVANCED FEATURES:
    - Free-flight variance reduction (config.free_flight_config)
    - GARF (Gaussian Artificial Response Function) support
    - Multi-head circular orbit acquisition
    - Distance-dependent spatial resolution
    - Custom material databases
    - Pytomography integration helpers

CONFIGURATION PATTERNS:
    # High resolution imaging
    config.detector_config.spatial_blur_fwhm = 0.2  # 2mm
    config.phantom_config.voxel_size = [0.1, 0.1, 0.1]

    # Fast acquisition
    config.acquisition_config.number_of_projections = 30
    config.acquisition_config.duration = 5
    config.number_of_threads = 8

    # Multi-isotope imaging
    config.detector_config.energy_windows = [
        {"name": "photopeak1", "min": 126.5, "max": 154.5},  # Tc-99m
        {"name": "photopeak2", "min": 200, "max": 240}       # In-111
    ]

NOTES:
    - SPECTConfig uses auto-created sub-configs (access via config.detector_config, etc.)
    - Don't create new DetectorConfig() manually - use the auto-created one
    - First run downloads Geant4 data files (~1-2 GB, one-time)
    - Visualization disabled by default for batch processing
    - Configuration can be serialized to JSON for reproducibility
    - Supports both image files and numpy arrays for phantom/activity

TROUBLESHOOTING:
    - If "missing required positional argument": Use auto-created configs
      (config.detector_config, not DetectorConfig())
    - If simulation fails to initialize: Check that phantom and source configs
      have compatible dimensions
    - For memory issues: Reduce phantom size or number of projections

REFERENCES:
    - OpenGATE: https://github.com/OpenGATE/opengate
    - SPECT Contrib: opengate/contrib/spect/
    - spect_config.py: High-level configuration classes
    - Documentation: http://opengate.readthedocs.io/

AUTHOR: Auto-generated example for GAGG_SPECT_SIM project
VERSION: 1.0
================================================================================
"""

import opengate as gate
from opengate.contrib.spect import spect_config
from pathlib import Path
import numpy as np


def create_spect_config_example():
    """
    Create SPECT simulation using high-level SPECTConfig class

    This demonstrates the configuration API with all major parameters.
    """

    print("=" * 70)
    print("SPECT Simulation using SPECTConfig Class")
    print("=" * 70)

    # =========================================================================
    # 1. Main SPECT Configuration
    # =========================================================================
    config = spect_config.SPECTConfig()

    # Basic simulation settings
    config.number_of_threads = 4
    config.random_seed = 42
    config.visu = False
    config.verbose = True

    print("\n✓ Main configuration initialized")

    # =========================================================================
    # 2. Detector Configuration
    # =========================================================================
    # Use the auto-created detector_config
    detector = config.detector_config

    # Choose detector model
    detector.model = "Intevo"  # Options: "Intevo" or "NM670"
    print(f"\n✓ Detector model: {detector.model}")

    # Collimator type
    detector.collimator = "lehr"  # Options: "lehr", "melp"/"megp", "he"/"hegp"
    print(f"  Collimator: {detector.collimator.upper()}")

    # For GE NM670, you can also specify crystal size
    if detector.model == "NM670":
        detector.crystal_size = "3/8"  # or "5/8"
        print(f"  Crystal size: {detector.crystal_size}\"")

    # Number of detector heads
    detector.number_of_heads = 2
    print(f"  Number of heads: {detector.number_of_heads}")

    # Digitizer configuration
    detector.energy_resolution = 0.07  # 7% at reference energy
    detector.energy_reference = 140.5  # keV
    print(f"  Energy resolution: {detector.energy_resolution*100:.1f}% @ {detector.energy_reference} keV")

    # Energy windows (photopeak ±10%)
    detector.energy_windows = [
        {"name": "photopeak", "min": 126.5, "max": 154.5}  # keV
    ]
    print(f"  Energy window: {detector.energy_windows[0]['min']}-{detector.energy_windows[0]['max']} keV")

    # Spatial blurring (effective pixel size)
    detector.spatial_blur_fwhm = 0.35  # cm
    print(f"  Spatial blur (pixel size): {detector.spatial_blur_fwhm} cm")

    # =========================================================================
    # 3. Acquisition Configuration
    # =========================================================================
    # Use the auto-created acquisition_config
    acquisition = config.acquisition_config

    # Gantry radius (distance from rotation center to detector)
    acquisition.radius = 36  # cm
    print(f"\n✓ Acquisition configuration:")
    print(f"  Gantry radius: {acquisition.radius} cm")

    # Rotation angles for circular orbit
    acquisition.number_of_projections = 60
    acquisition.start_angle_deg = 0
    acquisition.angular_span = 360  # degrees

    # Calculate angle step
    angle_step = acquisition.angular_span / acquisition.number_of_projections
    print(f"  Projections: {acquisition.number_of_projections}")
    print(f"  Angular span: {acquisition.angular_span}°")
    print(f"  Angle step: {angle_step:.2f}°")

    # Acquisition duration
    acquisition.duration = 20  # seconds
    print(f"  Duration: {acquisition.duration} seconds")

    # =========================================================================
    # 4. Phantom Configuration (FOV Definition)
    # =========================================================================
    # Use the auto-created phantom_config
    phantom = config.phantom_config

    # Create a simple voxelized phantom (or use existing image)
    # For this example, we'll create a water cylinder phantom

    # FOV size (defines the imaging region)
    fov_size = [40, 40, 40]  # cm [x, y, z]
    phantom.voxel_size = [0.4, 0.4, 0.4]  # cm - voxel resolution
    phantom.size = [int(fov_size[i] / phantom.voxel_size[i]) for i in range(3)]

    print(f"\n✓ Phantom (FOV) configuration:")
    print(f"  FOV size: {fov_size} cm")
    print(f"  Voxel size: {phantom.voxel_size} cm")
    print(f"  Matrix size: {phantom.size} voxels")

    # Phantom image path (if using existing image)
    # phantom.image_path = Path("path/to/phantom.mhd")

    # HU to material conversion
    phantom.hu_to_material_mode = "GateMaterials"
    phantom.density_tolerance = 0.05  # g/cm³

    # Phantom translation (position in world)
    phantom.translation = [0, 0, 0]  # cm

    # =========================================================================
    # 5. Source Configuration
    # =========================================================================
    # Use the auto-created source_config
    source = config.source_config

    # Radionuclide
    source.isotope = "Tc99m"
    print(f"\n✓ Source configuration:")
    print(f"  Isotope: {source.isotope}")

    # Total activity
    source.total_activity = 1e6  # Bq (1 MBq)
    print(f"  Total activity: {source.total_activity:.2e} Bq")

    # Activity distribution (voxelized)
    # Option 1: Create simple point source-like distribution
    activity_shape = phantom.size
    activity_image = np.zeros(activity_shape)

    # Put activity in center voxels (simulate point source)
    center = [s // 2 for s in activity_shape]
    activity_image[
        center[0]-2:center[0]+2,
        center[1]-2:center[1]+2,
        center[2]-2:center[2]+2
    ] = 1.0

    # Normalize
    activity_image = activity_image / np.sum(activity_image)

    source.activity_distribution = activity_image
    source.activity_voxel_size = phantom.voxel_size

    print(f"  Distribution: Centered point-like source")

    # Option 2: Use activity image file
    # source.activity_image_path = Path("path/to/activity.mhd")

    # =========================================================================
    # 6. Output Configuration
    # =========================================================================
    output_dir = Path("./output_spect_config")
    output_dir.mkdir(parents=True, exist_ok=True)

    config.output_dir = output_dir
    print(f"\n✓ Output directory: {output_dir}")

    # =========================================================================
    # 7. Create and Run Simulation
    # =========================================================================
    print("\n" + "=" * 70)
    print("Initializing simulation from config...")
    print("=" * 70)

    try:
        # Initialize simulation from config
        sim = config.initialize_simulation()

        print("\n✓ Simulation initialized successfully")
        print(f"  Threads: {config.number_of_threads}")
        print(f"  Random seed: {config.random_seed}")

        # Run simulation
        print("\n" + "=" * 70)
        print("Starting simulation...")
        print("=" * 70)

        sim.run()

        print("\n" + "=" * 70)
        print("Simulation completed successfully!")
        print("=" * 70)

        # Print output files
        print(f"\nOutput files saved to: {output_dir}")
        print("\nGenerated files:")
        for f in sorted(output_dir.glob("*")):
            print(f"  - {f.name}")

        return sim, config

    except Exception as e:
        print(f"\n❌ Simulation failed: {e}")
        import traceback
        traceback.print_exc()
        raise


def create_minimal_example():
    """
    Minimal example showing the simplest SPECT configuration

    This is useful for quick testing and understanding the basic API.
    """

    print("\n" + "=" * 70)
    print("Minimal SPECT Configuration Example")
    print("=" * 70)

    # Create config with default values
    config = spect_config.SPECTConfig()

    # Minimal detector setup (use auto-created config)
    config.detector_config.model = "Intevo"
    config.detector_config.collimator = "lehr"
    config.detector_config.number_of_heads = 1

    # Minimal acquisition (use auto-created config)
    config.acquisition_config.radius = 30  # cm
    config.acquisition_config.duration = 10  # seconds

    print("\n✓ Minimal configuration created")
    print(f"  Detector: {config.detector_config.model}")
    print(f"  Collimator: {config.detector_config.collimator}")
    print(f"  Radius: {config.acquisition_config.radius} cm")
    print(f"  Duration: {config.acquisition_config.duration} s")

    return config


def save_and_load_config_example():
    """
    Demonstrate saving and loading configuration to/from JSON

    This is useful for reproducibility and sharing configurations.
    """

    print("\n" + "=" * 70)
    print("Configuration Serialization Example")
    print("=" * 70)

    # Create a configuration
    config = spect_config.SPECTConfig()
    config.detector_config.model = "NM670"
    config.detector_config.collimator = "lehr"
    config.detector_config.crystal_size = "3/8"

    # Save to JSON
    config_file = Path("./spect_config_example.json")
    config.to_json(config_file)
    print(f"\n✓ Configuration saved to: {config_file}")

    # Load from JSON
    loaded_config = spect_config.SPECTConfig.from_json(config_file)
    print(f"✓ Configuration loaded from: {config_file}")
    print(f"  Detector: {loaded_config.detector_config.model}")
    print(f"  Collimator: {loaded_config.detector_config.collimator}")

    return config, loaded_config


def main():
    """Main execution function"""

    print("\n" + "=" * 70)
    print("OpenGATE SPECTConfig Examples")
    print("=" * 70)

    # Choose which example to run
    example_mode = "full"  # Options: "full", "minimal", "serialize"

    if example_mode == "full":
        # Full featured example
        sim, config = create_spect_config_example()

    elif example_mode == "minimal":
        # Minimal example (doesn't run simulation)
        config = create_minimal_example()
        print("\n(Simulation not run in minimal mode)")

    elif example_mode == "serialize":
        # Serialization example
        config, loaded_config = save_and_load_config_example()

    print("\n" + "=" * 70)
    print("Examples completed!")
    print("=" * 70)

    print("\n📖 Configuration Summary:")
    print("\nKey parameters you can customize:")
    print("\n1. Detector Configuration (DetectorConfig):")
    print("   - model: 'Intevo' or 'NM670'")
    print("   - collimator: 'lehr', 'melp', 'he'")
    print("   - crystal_size: '3/8' or '5/8' (for NM670)")
    print("   - number_of_heads: 1, 2, 3, etc.")
    print("   - energy_resolution: 0.07 (7%)")
    print("   - spatial_blur_fwhm: pixel size in cm")

    print("\n2. Acquisition Configuration (AcquisitionConfig):")
    print("   - radius: gantry radius in cm")
    print("   - number_of_projections: total projections")
    print("   - angular_span: rotation angle in degrees")
    print("   - duration: acquisition time in seconds")

    print("\n3. Phantom/FOV Configuration (PhantomConfig):")
    print("   - size: voxel matrix dimensions")
    print("   - voxel_size: voxel dimensions in cm")
    print("   - image_path: path to phantom image")
    print("   - translation: phantom position")

    print("\n4. Source Configuration (SourceConfig):")
    print("   - isotope: 'Tc99m', 'I131', etc.")
    print("   - total_activity: activity in Bq")
    print("   - activity_distribution: numpy array or image path")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
