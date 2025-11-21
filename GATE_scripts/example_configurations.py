#!/usr/bin/env python3
"""
GAGG SPECT Configuration Examples
==================================
Demonstrates various ways to configure the GAGG SPECT system.

Usage:
    python example_configurations.py --example 1
    python example_configurations.py --example 2 --run
    python example_configurations.py --custom

Author: Claude
Date: 2025-11-21
"""

import click
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
from gagg_spect_setup import create_simulation


# ==============================================================================
# Example 1: Default Small Animal Configuration
# ==============================================================================

def example_1_small_animal():
    """
    Example 1: Default small animal SPECT setup
    - 3 detector heads with pinhole collimators
    - 160×160 GAGG crystal array (3mm crystals)
    - 10 cm FOV
    - Tc-99m source
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Small Animal SPECT (Default)")
    print("="*70)

    # Use built-in preset
    config = SPECTConfig.default_small_animal()

    # Display configuration
    config.print_summary()

    # Save to file
    config.to_json("config_example1_small_animal.json")
    print("💾 Saved to: config_example1_small_animal.json\n")

    return config


# ==============================================================================
# Example 2: High-Resolution Small Animal
# ==============================================================================

def example_2_high_resolution():
    """
    Example 2: High-resolution small animal imaging
    - Smaller crystals (2mm instead of 3mm)
    - Smaller pinhole (1mm)
    - Denser array (200×200)
    - Closer detector positioning
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: High-Resolution Small Animal SPECT")
    print("="*70)

    config = SPECTConfig(
        name="GAGG_SPECT_HighRes",
        output_dir="output_highres",

        # High-resolution scintillator
        detector=DetectorConfig(
            number_of_heads=3,
            scintillator=ScintillatorConfig(
                crystal_size_x=2.0,  # Smaller crystals
                crystal_size_y=2.0,
                crystal_thickness=12.0,  # Thicker for better efficiency
                crystal_spacing=0.05,  # Tighter spacing
                array_size_x=200,  # More crystals
                array_size_y=200,
                material="GAGG",
            ),
            collimator=CollimatorConfig(
                type="pinhole",
                material="Tungsten",
                thickness=8.0,  # Thicker collimator
                pinhole_diameter=1.0,  # Smaller pinhole for better resolution
            ),
        ),

        # Small FOV
        fov=FOVConfig(
            radius=4.0,  # 8 cm diameter
            height=8.0,
            detector_radius=8.0,  # Closer to object
            name="ultra_small_fov_8cm",
        ),

        # Longer acquisition for better statistics
        acquisition=AcquisitionConfig(
            duration=120.0,  # 2 minutes
            rotation_enabled=True,
            number_of_projections=90,
        ),
    )

    config.print_summary()
    config.to_json("config_example2_highres.json")
    print("💾 Saved to: config_example2_highres.json\n")

    return config


# ==============================================================================
# Example 3: Clinical Parallel-Hole System
# ==============================================================================

def example_3_clinical():
    """
    Example 3: Clinical SPECT with parallel-hole collimation
    - 2 detector heads (opposed)
    - Parallel-hole collimator
    - Large FOV (80 cm)
    - Standard clinical parameters
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Clinical SPECT with Parallel Collimation")
    print("="*70)

    config = SPECTConfig(
        name="GAGG_SPECT_Clinical",
        output_dir="output_clinical",

        detector=DetectorConfig(
            number_of_heads=2,  # Dual-head system
            scintillator=ScintillatorConfig(
                crystal_size_x=4.0,  # Larger crystals for clinical
                crystal_size_y=4.0,
                crystal_thickness=15.0,
                crystal_spacing=0.2,
                array_size_x=150,
                array_size_y=150,
            ),
            collimator=CollimatorConfig(
                type="parallel",  # Parallel-hole collimator
                material="Lead",
                parallel_hole_diameter=1.5,
                parallel_septa_thickness=0.2,
                parallel_hole_length=35.0,  # LEHR-like
            ),
        ),

        # Large clinical FOV
        fov=FOVConfig.large_fov(),

        # Standard clinical acquisition
        acquisition=AcquisitionConfig(
            duration=300.0,  # 5 minutes
            rotation_enabled=True,
            number_of_projections=120,
        ),
    )

    config.print_summary()
    config.to_json("config_example3_clinical.json")
    print("💾 Saved to: config_example3_clinical.json\n")

    return config


# ==============================================================================
# Example 4: Multi-Isotope Imaging
# ==============================================================================

def example_4_multi_isotope():
    """
    Example 4: Configuration for I-123 imaging
    - Different energy (159 keV)
    - Adjusted energy window
    - Optimized for thyroid imaging
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: I-123 Thyroid Imaging")
    print("="*70)

    config = SPECTConfig.default_small_animal()
    config.name = "GAGG_SPECT_I123"
    config.output_dir = "output_i123"

    # Change source to I-123
    config.source = SourceConfig(
        isotope="I123",
        energy=159.0,  # keV
        activity=5e6,  # 5 MBq
        geometry_type="sphere",
        geometry_radius=5.0,  # mm (simulated thyroid)
    )

    # Adjust energy window for I-123
    config.digitizer.energy_reference = 159.0
    config.digitizer.energy_window_min = 143.0  # ±10%
    config.digitizer.energy_window_max = 175.0

    config.print_summary()
    config.to_json("config_example4_i123.json")
    print("💾 Saved to: config_example4_i123.json\n")

    return config


# ==============================================================================
# Example 5: Custom Crystal Dimensions
# ==============================================================================

def example_5_custom_crystals():
    """
    Example 5: Testing different crystal dimensions
    - Various crystal sizes
    - Demonstrates flexibility of configuration system
    """
    print("\n" + "="*70)
    print("EXAMPLE 5: Custom Crystal Dimensions")
    print("="*70)

    # Test different crystal configurations
    crystal_configs = [
        {"size": 1.5, "thickness": 8.0, "array": 250, "name": "micro"},
        {"size": 3.0, "thickness": 10.0, "array": 160, "name": "standard"},
        {"size": 5.0, "thickness": 15.0, "array": 100, "name": "large"},
    ]

    configs = []
    for cfg in crystal_configs:
        config = SPECTConfig(
            name=f"GAGG_SPECT_{cfg['name']}_crystals",
            output_dir=f"output_{cfg['name']}",
            detector=DetectorConfig(
                number_of_heads=3,
                scintillator=ScintillatorConfig(
                    crystal_size_x=cfg["size"],
                    crystal_size_y=cfg["size"],
                    crystal_thickness=cfg["thickness"],
                    array_size_x=cfg["array"],
                    array_size_y=cfg["array"],
                ),
            ),
            fov=FOVConfig.small_fov(),
        )

        print(f"\n--- {cfg['name'].upper()} Crystal Configuration ---")
        print(f"  Crystal size: {cfg['size']} × {cfg['size']} × {cfg['thickness']} mm³")
        print(f"  Array: {cfg['array']} × {cfg['array']} = {cfg['array']**2:,} crystals")
        print(f"  Detector size: {config.detector.scintillator.detector_size_x:.1f} mm")

        configs.append(config)
        config.to_json(f"config_example5_{cfg['name']}.json")

    print("\n💾 Saved 3 configurations with different crystal sizes\n")
    return configs


# ==============================================================================
# Example 6: FOV Comparison
# ==============================================================================

def example_6_fov_comparison():
    """
    Example 6: Compare different FOV configurations
    - Small, Medium, Large FOV presets
    - Same detector configuration
    """
    print("\n" + "="*70)
    print("EXAMPLE 6: FOV Size Comparison")
    print("="*70)

    fov_presets = [
        ("small", FOVConfig.small_fov()),
        ("medium", FOVConfig.medium_fov()),
        ("large", FOVConfig.large_fov()),
    ]

    configs = []
    for name, fov in fov_presets:
        config = SPECTConfig.default_small_animal()
        config.name = f"GAGG_SPECT_{name}_FOV"
        config.output_dir = f"output_{name}_fov"
        config.fov = fov

        print(f"\n--- {name.upper()} FOV ---")
        print(f"  Diameter: {fov.diameter} cm")
        print(f"  Height: {fov.height} cm")
        print(f"  Detector radius: {fov.detector_radius} cm")

        configs.append(config)
        config.to_json(f"config_example6_{name}_fov.json")

    print("\n💾 Saved 3 FOV comparison configurations\n")
    return configs


# ==============================================================================
# Example 7: Load and Modify Existing Configuration
# ==============================================================================

def example_7_load_and_modify():
    """
    Example 7: Load existing configuration and modify it
    - Demonstrates configuration modification workflow
    """
    print("\n" + "="*70)
    print("EXAMPLE 7: Load and Modify Configuration")
    print("="*70)

    # Create base configuration
    base_config = SPECTConfig.default_small_animal()
    base_config.to_json("config_base.json")
    print("✅ Created base configuration: config_base.json")

    # Load and modify
    modified_config = SPECTConfig.from_json("config_base.json")

    # Make modifications
    modified_config.name = "GAGG_SPECT_Modified"
    modified_config.detector.scintillator.crystal_thickness = 12.0  # Thicker crystals
    modified_config.acquisition.duration = 120.0  # Longer acquisition
    modified_config.source.activity = 2e6  # Higher activity

    print("\n✅ Modified configuration:")
    print(f"  Crystal thickness: 10.0 → 12.0 mm")
    print(f"  Acquisition time: 60.0 → 120.0 s")
    print(f"  Source activity: 1.0e6 → 2.0e6 Bq")

    modified_config.to_json("config_modified.json")
    print("\n💾 Saved modified configuration: config_modified.json\n")

    return modified_config


# ==============================================================================
# Main CLI
# ==============================================================================

@click.command()
@click.option(
    "--example",
    type=click.IntRange(1, 7),
    help="Run specific example (1-7)",
)
@click.option(
    "--all",
    is_flag=True,
    help="Generate all example configurations",
)
@click.option(
    "--run",
    is_flag=True,
    help="Run simulation after generating configuration",
)
@click.option(
    "--visu",
    is_flag=True,
    help="Enable visualization (requires --run)",
)
def main(example, all, run, visu):
    """
    Generate example GAGG SPECT configurations

    Examples:
        python example_configurations.py --example 1
        python example_configurations.py --example 2 --run
        python example_configurations.py --all
        python example_configurations.py --example 1 --run --visu
    """

    examples = {
        1: example_1_small_animal,
        2: example_2_high_resolution,
        3: example_3_clinical,
        4: example_4_multi_isotope,
        5: example_5_custom_crystals,
        6: example_6_fov_comparison,
        7: example_7_load_and_modify,
    }

    if all:
        print("\n" + "="*70)
        print("Generating ALL Example Configurations")
        print("="*70)

        for i, func in examples.items():
            config = func()

        print("\n" + "="*70)
        print("✅ All examples generated successfully!")
        print("="*70)
        print("\nGenerated files:")
        import pathlib
        for json_file in sorted(pathlib.Path(".").glob("config_example*.json")):
            print(f"  - {json_file}")
        print()

    elif example:
        # Run specific example
        config = examples[example]()

        if run:
            print("\n" + "="*70)
            print(f"Running Simulation for Example {example}")
            print("="*70 + "\n")

            sim = create_simulation(config, visu=visu)
            sim.run()

            print("\n✅ Simulation completed!")
    else:
        # Show help
        print("\n" + "="*70)
        print("GAGG SPECT Configuration Examples")
        print("="*70)
        print("\nAvailable examples:")
        print("  1. Small animal SPECT (default)")
        print("  2. High-resolution small animal")
        print("  3. Clinical parallel-hole system")
        print("  4. Multi-isotope imaging (I-123)")
        print("  5. Custom crystal dimensions")
        print("  6. FOV size comparison")
        print("  7. Load and modify configuration")
        print("\nUsage:")
        print("  python example_configurations.py --example <1-7>")
        print("  python example_configurations.py --all")
        print("  python example_configurations.py --example 1 --run --visu")
        print("\nFor more options, run: python example_configurations.py --help\n")


if __name__ == "__main__":
    main()
