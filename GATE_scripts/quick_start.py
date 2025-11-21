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

# Add GAGG detector heads (3 heads, pinhole, small animal FOV)
heads, crystals = gagg.add_gagg_spect_heads(
    sim,
    number_of_heads=3,
    collimator_type="pinhole",
    fov_preset="small_animal"
)

# Add digitizer for each head
for i, crystal in enumerate(crystals):
    gagg.add_gagg_digitizer(sim, crystal.name, name=f"head_{i}")

# Add Tc-99m point source at center
keV = gate.g4_units.keV
Bq = gate.g4_units.Bq

source = sim.add_source("GenericSource", "tc99m")
source.particle = "gamma"
source.energy.mono = 140.5 * keV
source.activity = 1e6 * Bq  # 1 MBq
source.position.type = "point"
source.position.translation = [0, 0, 0]  # Center of FOV
source.direction.type = "iso"  # Isotropic emission

# Physics configuration
sim.physics_manager.physics_list_name = "G4EmStandardPhysics_option4"

# Run timing (1 second simulation)
sim.run_timing_intervals = [[0, 1 * gate.g4_units.second]]

print("Setup complete. Running simulation...\n")

sim.run()

print("\n" + "="*70)
print("Simulation completed!")
print("="*70)
print("\nOutput files:")
print("  head_0_hits.root, head_1_hits.root, head_2_hits.root")
print("  head_0_projection.mhd/.raw, head_1_projection.mhd/.raw, ...")
print("\n")
