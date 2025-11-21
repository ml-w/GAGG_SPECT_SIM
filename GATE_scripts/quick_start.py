import opengate as gate
import gagg_spect_detector as gagg

# Create simulation
sim = gate.Simulation()
sim.world.size = [100 * gate.g4_units.cm] * 3
sim.world.material = "G4_AIR"

# Add GAGG detector (configurable via JSON or params)
heads, crystals = gagg.add_gagg_spect_heads(
    sim,
    number_of_heads=3,
    collimator_type="pinhole",
    fov_preset="small_animal"
)

# Add digitizer
for i, crystal in enumerate(crystals):
    gagg.add_gagg_digitizer(sim, crystal.name, name=f"head_{i}")

# Run
sim.run()
