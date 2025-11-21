#!/usr/bin/env python3
"""
Example: GAGG SPECT with OpenGATE SPECTConfig
==============================================
Demonstrates how to use the custom GAGG SPECT detector
with the OpenGATE configuration system.

This follows the OpenGATE pattern where you:
1. Import SPECTConfig from opengate.contrib.spect
2. Use custom detector model (gagg_spect_detector.py)
3. Configure through geometric parameters JSON

Usage:
    python example_gagg_spect.py --preset small_animal
    python example_gagg_spect.py --preset medium --heads 2
    python example_gagg_spect.py --custom

Author: Claude
Date: 2025-11-21
"""

import opengate as gate
import click
import json
from pathlib import Path

# Import GAGG detector module
import gagg_spect_detector as gagg


# ==============================================================================
# Example 1: Using Default Parameters
# ==============================================================================

def example_default_configuration():
    """
    Example 1: Create GAGG SPECT simulation with default parameters
    """
    print("\n" + "="*70)
    print("Example 1: Default GAGG SPECT Configuration")
    print("="*70)

    # Create simulation
    sim = gate.Simulation()

    # World
    cm = gate.g4_units.cm
    sim.world.size = [100 * cm, 100 * cm, 100 * cm]
    sim.world.material = "G4_AIR"

    # Add GAGG detector heads (uses default parameters from JSON)
    heads, crystals = gagg.add_gagg_spect_heads(
        sim,
        number_of_heads=3,
        collimator_type="pinhole",
        fov_preset="small_animal",
        debug=False
    )

    print(f"\n✅ Created {len(heads)} detector heads")
    print(f"   Crystal array: 160×160")
    print(f"   Collimator: pinhole")
    print(f"   FOV: small_animal (10 cm diameter)")

    # Add digitizer for each head
    for i, crystal in enumerate(crystals):
        gagg.add_gagg_digitizer(
            sim,
            crystal.name,
            name=f"head_{i}",
            output_filename=f"output/gagg_head_{i}"
        )

    print(f"✅ Added digitizers for {len(crystals)} heads")

    # Add simple point source
    keV = gate.g4_units.keV
    Bq = gate.g4_units.Bq
    mm = gate.g4_units.mm

    source = sim.add_source("GenericSource", "tc99m")
    source.particle = "gamma"
    source.energy.mono = 140.5 * keV
    source.activity = 1e6 * Bq
    source.position.type = "point"
    source.direction.type = "iso"

    print("✅ Added Tc-99m point source (1 MBq)")

    # Physics
    sim.physics_manager.physics_list_name = "G4EmStandardPhysics_option4"

    # Timing
    sim.run_timing_intervals = [[0, 60 * gate.g4_units.second]]

    print("\n✅ Simulation configured (60 second acquisition)")

    return sim


# ==============================================================================
# Example 2: Custom Scintillator Dimensions
# ==============================================================================

def example_custom_crystal_size():
    """
    Example 2: Modify crystal dimensions programmatically
    """
    print("\n" + "="*70)
    print("Example 2: Custom Crystal Dimensions")
    print("="*70)

    # Load default parameters
    params = gagg.get_geometrical_parameters()

    # Modify crystal dimensions
    params.crystal_size_x_mm = 2.0  # 2mm instead of 3mm
    params.crystal_size_y_mm = 2.0
    params.crystal_thickness_mm = 12.0  # 12mm instead of 10mm
    params.crystal_array_size_x = 200  # 200×200 instead of 160×160
    params.crystal_array_size_y = 200

    # Recalculate detector size
    pixel_pitch = params.crystal_size_x_mm + params.crystal_spacing_mm
    params.detector_size_x_mm = params.crystal_array_size_x * pixel_pitch
    params.detector_size_y_mm = params.crystal_array_size_y * pixel_pitch

    print(f"\n📐 Custom crystal configuration:")
    print(f"   Crystal size: {params.crystal_size_x_mm} × {params.crystal_size_y_mm} × {params.crystal_thickness_mm} mm")
    print(f"   Array: {params.crystal_array_size_x} × {params.crystal_array_size_y}")
    print(f"   Detector size: {params.detector_size_x_mm} × {params.detector_size_y_mm} mm")
    print(f"   Total crystals: {params.crystal_array_size_x * params.crystal_array_size_y:,}")

    # Create simulation with custom parameters
    sim = gate.Simulation()
    cm = gate.g4_units.cm
    sim.world.size = [100 * cm, 100 * cm, 100 * cm]
    sim.world.material = "G4_AIR"

    # Add detector with custom parameters
    heads, crystals = gagg.add_gagg_spect_heads(
        sim,
        number_of_heads=3,
        collimator_type="pinhole",
        fov_preset="small_animal",
        params=params  # Pass custom parameters
    )

    print(f"\n✅ Created detector with custom crystal dimensions")

    return sim, params


# ==============================================================================
# Example 3: Different FOV Configurations
# ==============================================================================

def example_different_fov(fov_preset="small_animal"):
    """
    Example 3: Use different FOV presets
    """
    print("\n" + "="*70)
    print(f"Example 3: FOV Configuration - {fov_preset}")
    print("="*70)

    params = gagg.get_geometrical_parameters()

    # Display FOV info
    fov_config = params.fov_presets[fov_preset]
    print(f"\n🎯 FOV Configuration: {fov_config.description}")
    print(f"   Diameter: {fov_config.fov_radius_cm * 2} cm")
    print(f"   Height: {fov_config.fov_height_cm} cm")
    print(f"   Detector radius: {fov_config.detector_radius_cm} cm")

    # Create simulation
    sim = gate.Simulation()
    cm = gate.g4_units.cm
    world_size = max(200 * cm, fov_config.detector_radius_cm * 3 * cm)
    sim.world.size = [world_size, world_size, world_size]
    sim.world.material = "G4_AIR"

    # Add FOV phantom (water cylinder for reference)
    fov = sim.add_volume("Cylinder", "FOV")
    fov.rmax = fov_config.fov_radius_cm * cm
    fov.rmin = 0
    fov.height = fov_config.fov_height_cm * cm
    fov.material = "G4_WATER"
    fov.color = [0, 1, 1, 0.2]
    fov.translation = [0, 0, 0]

    print(f"✅ Added FOV phantom (Ø{fov_config.fov_radius_cm * 2} cm × {fov_config.fov_height_cm} cm)")

    # Add detector heads
    heads, crystals = gagg.add_gagg_spect_heads(
        sim,
        number_of_heads=3,
        collimator_type="pinhole",
        fov_preset=fov_preset
    )

    print(f"✅ Added {len(heads)} detector heads at {fov_config.detector_radius_cm} cm radius")

    return sim


# ==============================================================================
# Example 4: Parallel-Hole Collimator
# ==============================================================================

def example_parallel_collimator():
    """
    Example 4: Use parallel-hole collimator instead of pinhole
    """
    print("\n" + "="*70)
    print("Example 4: Parallel-Hole Collimator Configuration")
    print("="*70)

    params = gagg.get_geometrical_parameters()

    print(f"\n🔍 Parallel collimator parameters:")
    print(f"   Hole diameter: {params.parallel_hole_diameter_mm} mm")
    print(f"   Septa thickness: {params.parallel_septa_thickness_mm} mm")
    print(f"   Hole length: {params.parallel_hole_length_mm} mm")

    # Create simulation
    sim = gate.Simulation()
    cm = gate.g4_units.cm
    sim.world.size = [100 * cm, 100 * cm, 100 * cm]
    sim.world.material = "G4_AIR"

    # Add detector with parallel collimator
    heads, crystals = gagg.add_gagg_spect_heads(
        sim,
        number_of_heads=2,  # Dual-head for parallel
        collimator_type="parallel",
        fov_preset="small_animal"
    )

    print(f"\n✅ Created {len(heads)} heads with parallel-hole collimators")

    return sim


# ==============================================================================
# Example 5: Saving Custom Configuration
# ==============================================================================

def example_save_custom_config():
    """
    Example 5: Create and save custom geometric parameters
    """
    print("\n" + "="*70)
    print("Example 5: Save Custom Configuration")
    print("="*70)

    # Load default parameters
    params = gagg.get_geometrical_parameters()

    # Create custom configuration
    custom_config = {
        "detector_name": "GAGG_SPECT_Custom_HighRes",
        "description": "High-resolution custom configuration",

        "crystal_size_x_mm": 1.5,  # Smaller crystals
        "crystal_size_y_mm": 1.5,
        "crystal_thickness_mm": 15.0,  # Thicker
        "crystal_spacing_mm": 0.05,  # Tighter spacing
        "crystal_array_size_x": 250,  # More crystals
        "crystal_array_size_y": 250,
        "crystal_material": "GAGG",

        "detector_size_x_mm": 387.5,  # Computed: 250 * (1.5 + 0.05)
        "detector_size_y_mm": 387.5,

        "collimator_type": "pinhole",
        "collimator_material": "Tungsten",
        "collimator_thickness_mm": 8.0,  # Thicker collimator
        "pinhole_diameter_mm": 1.0,  # Smaller pinhole
        "pinhole_opening_angle_deg": 25.0,

        "parallel_hole_diameter_mm": 1.2,
        "parallel_septa_thickness_mm": 0.15,
        "parallel_hole_length_mm": 30.0,

        "shielding_material": "Lead",
        "shielding_thickness_mm": 5.0,

        "backside_thickness_mm": 50.0,
        "backside_material": "Glass",

        "fov_presets": params.fov_presets,  # Keep existing presets

        "energy_resolution_fwhm": 0.06,  # Better resolution
        "energy_reference_keV": 140.5,
        "energy_window_lower_keV": 126.5,
        "energy_window_upper_keV": 154.5,

        "default_preset": "small_animal"
    }

    # Save to file
    output_file = "gagg_spect_custom_parameters.json"
    with open(output_file, "w") as f:
        json.dump(custom_config, f, indent=2)

    print(f"\n💾 Saved custom configuration to: {output_file}")
    print(f"\n📐 Custom specifications:")
    print(f"   Crystal: {custom_config['crystal_size_x_mm']} × {custom_config['crystal_size_y_mm']} × {custom_config['crystal_thickness_mm']} mm")
    print(f"   Array: {custom_config['crystal_array_size_x']} × {custom_config['crystal_array_size_y']}")
    print(f"   Total crystals: {custom_config['crystal_array_size_x'] * custom_config['crystal_array_size_y']:,}")
    print(f"   Pinhole: {custom_config['pinhole_diameter_mm']} mm")
    print(f"   Energy resolution: {custom_config['energy_resolution_fwhm']*100}%")

    print(f"\nTo use this configuration:")
    print(f'  params_file = "{output_file}"')
    print(f'  with open(params_file) as f:')
    print(f'      custom_params = json.load(f)')
    print(f'      custom_params = Box(custom_params)')
    print(f'  gagg.add_gagg_spect_heads(sim, params=custom_params)')


# ==============================================================================
# Main CLI
# ==============================================================================

@click.command()
@click.option(
    "--preset",
    type=click.Choice(["small_animal", "medium", "large_clinical"]),
    default="small_animal",
    help="FOV preset to use"
)
@click.option(
    "--heads",
    type=click.IntRange(1, 4),
    default=3,
    help="Number of detector heads (1-4)"
)
@click.option(
    "--collimator",
    type=click.Choice(["pinhole", "parallel"]),
    default="pinhole",
    help="Collimator type"
)
@click.option(
    "--custom",
    is_flag=True,
    help="Run custom crystal size example"
)
@click.option(
    "--save-config",
    is_flag=True,
    help="Save custom configuration template"
)
@click.option(
    "--run",
    is_flag=True,
    help="Run the simulation (otherwise just configure)"
)
@click.option(
    "--visu",
    is_flag=True,
    help="Enable visualization"
)
def main(preset, heads, collimator, custom, save_config, run, visu):
    """
    Create and optionally run GAGG SPECT simulation with custom configuration

    Examples:
        python example_gagg_spect.py --preset small_animal
        python example_gagg_spect.py --preset medium --heads 2 --collimator parallel
        python example_gagg_spect.py --custom
        python example_gagg_spect.py --save-config
        python example_gagg_spect.py --preset small_animal --run --visu
    """

    print("\n" + "="*70)
    print("GAGG SPECT Example with OpenGATE")
    print("="*70)

    if save_config:
        example_save_custom_config()
        return

    if custom:
        sim, params = example_custom_crystal_size()
    else:
        # Load parameters
        params = gagg.get_geometrical_parameters()

        print(f"\n📊 Configuration:")
        print(f"   FOV preset: {preset}")
        print(f"   Number of heads: {heads}")
        print(f"   Collimator: {collimator}")
        print(f"   Crystal: {params.crystal_size_x_mm} × {params.crystal_size_y_mm} × {params.crystal_thickness_mm} mm")
        print(f"   Array: {params.crystal_array_size_x} × {params.crystal_array_size_y}")

        # Create simulation
        sim = gate.Simulation()
        cm = gate.g4_units.cm

        # Get FOV config for world size
        fov_config = params.fov_presets[preset]
        world_size = max(200 * cm, fov_config.detector_radius_cm * 3 * cm)
        sim.world.size = [world_size, world_size, world_size]
        sim.world.material = "G4_AIR"

        # Add FOV phantom
        fov = sim.add_volume("Cylinder", "FOV")
        fov.rmax = fov_config.fov_radius_cm * cm
        fov.rmin = 0
        fov.height = fov_config.fov_height_cm * cm
        fov.material = "G4_WATER"
        fov.color = [0, 1, 1, 0.2]

        # Add detector heads
        heads_list, crystals = gagg.add_gagg_spect_heads(
            sim,
            number_of_heads=heads,
            collimator_type=collimator,
            fov_preset=preset
        )

        # Add digitizers
        for i, crystal in enumerate(crystals):
            gagg.add_gagg_digitizer(
                sim,
                crystal.name,
                name=f"head_{i}",
                output_filename=f"output/gagg_head_{i}"
            )

        # Add source
        keV = gate.g4_units.keV
        Bq = gate.g4_units.Bq

        source = sim.add_source("GenericSource", "tc99m")
        source.particle = "gamma"
        source.energy.mono = 140.5 * keV
        source.activity = 1e6 * Bq
        source.position.type = "point"
        source.direction.type = "iso"

        # Physics
        sim.physics_manager.physics_list_name = "G4EmStandardPhysics_option4"

        # Timing
        sim.run_timing_intervals = [[0, 60 * gate.g4_units.second]]

        print(f"\n✅ Simulation configured successfully!")

    # Run simulation if requested
    if run:
        print("\n" + "="*70)
        print("Running Simulation")
        print("="*70)

        sim.visu = visu
        if visu:
            sim.visu_type = "qt"

        sim.run()

        print("\n✅ Simulation completed!")
    else:
        print("\n💡 Configuration created. Use --run to execute simulation.")


if __name__ == "__main__":
    main()
