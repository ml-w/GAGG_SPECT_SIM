#!/usr/bin/env python3
"""
Advanced Example using OpenGATE SPECTConfig Class

This example demonstrates the high-level SPECTConfig API for comprehensive
SPECT simulation configuration including:
- Detector configuration (model, collimator, crystal)
- Phantom configuration (voxelized)
- Source configuration (activity distribution)
- Acquisition configuration (gantry rotation, multiple heads)
- Field of View (FOV) customization

Installation:
    pip install opengate

Usage:
    python example_spect_config.py
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
