#!/usr/bin/env python3
"""
VISUALIZATION ONLY - Geometry Check
====================================
This script only visualizes geometry without running simulation.

Translated from GATE 9 macro to GATE 10 Python
"""

import opengate as gate
from geom_spect import setup_geometry


def main():
    """Main function to visualize SPECT geometry."""

    # Units
    cm = gate.g4_units.cm

    # Create simulation
    sim = gate.Simulation()
    sim.random_engine = "MersenneTwister"
    sim.random_seed = "auto"
    sim.check_volumes_overlap = True
    sim.g4_verbose = False
    sim.number_of_threads = 1
    sim.output_dir = "output"

    # =====================================================
    # VISUALIZATION SETTINGS
    # =====================================================
    sim.visu = True
    sim.visu_type = "qt"  # Use Qt visualization
    # Alternative: sim.visu_type = "vrml" for file export

    # Visualization parameters (Qt viewer settings)
    sim.visu_verbose = False

    # =====================================================
    # SETUP GEOMETRY
    # =====================================================
    # Using small FOV configuration for faster rendering
    crystal = setup_geometry(
        sim,
        detector_radius=30,  # cm
        fov_radius=5,        # cm (small FOV)
        fov_height=10,       # cm
        num_heads=2          # Dual-head system
    )

    # =====================================================
    # PHYSICS (minimal for visualization)
    # =====================================================
    sim.physics_manager.physics_list_name = "G4EmStandardPhysics_option4"

    # =====================================================
    # RUN VISUALIZATION
    # =====================================================
    # Note: In GATE 10, visualization is integrated into the run
    # The Qt viewer will open automatically when sim.visu = True

    print("Starting visualization...")
    print("Close the Qt viewer window to exit.")

    # Initialize and run (for visualization only)
    sim.run(start_new_process=False)

    print("Visualization complete.")


def export_geometry_vrml():
    """
    Alternative function to export geometry to VRML file.
    Useful when Qt display is not available.
    """

    # Units
    cm = gate.g4_units.cm

    # Create simulation
    sim = gate.Simulation()
    sim.random_engine = "MersenneTwister"
    sim.random_seed = "auto"
    sim.check_volumes_overlap = True
    sim.g4_verbose = False
    sim.number_of_threads = 1
    sim.output_dir = "output"

    # Use VRML export instead of Qt
    sim.visu = True
    sim.visu_type = "vrml"
    # sim.visu_filename = "geometry_spect.wrl"

    # Setup geometry
    crystal = setup_geometry(
        sim,
        detector_radius=30,
        fov_radius=5,
        fov_height=10,
        num_heads=2
    )

    # Physics
    # sim.physics_manager.physics_list_name = "G4EmStandardPhysics_option4"

    # Run to generate VRML file
    sim.run()

    print(f"Geometry exported to: {sim.output_dir}/{sim.visu_filename}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--vrml":
        export_geometry_vrml()
    else:
        main()
