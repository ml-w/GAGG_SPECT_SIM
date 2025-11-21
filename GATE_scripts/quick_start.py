#!/usr/bin/env python3
"""
Quick Start Example for GAGG SPECT Simulation
==============================================
Minimal working example to get started quickly.

This script creates a 3-head GAGG SPECT system with:
- Pinhole collimation
- Small animal FOV (10 cm diameter)
- Tc-99m point source at center
- 1 second simulation time

Usage:
    python quick_start.py

Author: Claude
Date: 2025-11-21
"""

import opengate as gate
import gagg_spect_detector as gagg

print("\n" + "="*70)
print("GAGG SPECT Quick Start")
print("="*70)

# Create simulation
sim = gate.Simulation()

# World volume
cm = gate.g4_units.cm
sim.world.size = [100 * cm, 100 * cm, 100 * cm]
sim.world.material = "G4_AIR"

print("\n✅ Simulation world created (100 cm³)")

# Add GAGG detector heads (3 heads, pinhole, small animal FOV)
heads, crystals = gagg.add_gagg_spect_heads(
    sim,
    number_of_heads=3,
    collimator_type="pinhole",
    fov_preset="small_animal"
)

print(f"✅ Added {len(heads)} GAGG detector heads")
print(f"   - Collimator: pinhole (1.5 mm aperture)")
print(f"   - FOV: small_animal (10 cm diameter)")
print(f"   - Crystal array: 160 × 160 per head")

# Add digitizer for each head
for i, crystal in enumerate(crystals):
    gagg.add_gagg_digitizer(sim, crystal.name, name=f"head_{i}")

print(f"✅ Added digitizer chains for {len(crystals)} heads")

# Add Tc-99m point source at center
keV = gate.g4_units.keV
Bq = gate.g4_units.Bq
mm = gate.g4_units.mm

source = sim.add_source("GenericSource", "tc99m")
source.particle = "gamma"
source.energy.mono = 140.5 * keV
source.activity = 1e6 * Bq  # 1 MBq
source.position.type = "point"
source.position.translation = [0, 0, 0]  # Center of FOV
source.direction.type = "iso"  # Isotropic emission

print("✅ Added Tc-99m point source")
print(f"   - Energy: 140.5 keV")
print(f"   - Activity: 1 MBq")
print(f"   - Position: center (0, 0, 0)")

# Physics configuration
sim.physics_manager.physics_list_name = "G4EmStandardPhysics_option4"
print("✅ Physics: G4EmStandardPhysics_option4")

# Run timing (1 second simulation)
sim.run_timing_intervals = [[0, 1 * gate.g4_units.second]]
print("✅ Simulation time: 1 second")

# Run simulation
print("\n" + "="*70)
print("Running simulation...")
print("="*70 + "\n")

sim.run()

print("\n" + "="*70)
print("✅ Simulation completed successfully!")
print("="*70)
print("\nOutput files should be generated in the current directory:")
print("  - head_0_hits.root, head_1_hits.root, head_2_hits.root")
print("  - head_0_projection.mhd/.raw, etc.")
print("\nTo visualize projections:")
print("  python convert_mhd_to_png.py head_0_projection.mhd")
print("\nFor more examples:")
print("  python example_gagg_spect.py --help")
print("="*70 + "\n")
