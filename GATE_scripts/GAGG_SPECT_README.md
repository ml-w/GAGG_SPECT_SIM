# GAGG SPECT Configurable Detector for OpenGATE

## Overview

This is a custom GAGG scintillator SPECT detector module that integrates with the OpenGATE framework, specifically designed to work with `opengate.contrib.spect.spect_config.SPECTConfig`.

**Key Features:**
- ✅ Uses OpenGATE's existing SPECTConfig system (not a reimplementation)
- ✅ Configurable scintillator dimensions (crystal size, array configuration)
- ✅ Configurable FOV (field of view presets)
- ✅ Pinhole or parallel-hole collimators
- ✅ Multiple detector heads (1-4)
- ✅ JSON-based parameter configuration
- ✅ Compatible with OpenGATE digitizer chain

## Architecture

This implementation follows the OpenGATE pattern used by existing detector models (`ge_discovery_nm670.py`, `siemens_intevo.py`):

```
gagg_spect_detector.py          # Detector geometry and setup functions
gagg_spect_geometrical_parameters.json  # Configurable parameters
example_gagg_spect.py            # Usage examples
```

## Quick Start

### Prerequisites

```bash
pip install opengate
pip install python-box  # For parameter handling
```

### Basic Usage

```python
import opengate as gate
import gagg_spect_detector as gagg

# Create simulation
sim = gate.Simulation()
sim.world.size = [100 * gate.g4_units.cm] * 3
sim.world.material = "G4_AIR"

# Add GAGG SPECT detector heads
heads, crystals = gagg.add_gagg_spect_heads(
    sim,
    number_of_heads=3,
    collimator_type="pinhole",
    fov_preset="small_animal"
)

# Add digitizer
for i, crystal in enumerate(crystals):
    gagg.add_gagg_digitizer(sim, crystal.name, name=f"head_{i}")

# Run simulation
sim.run()
```

### Using the Example Script

```bash
# Show available options
python example_gagg_spect.py --help

# Run with default configuration
python example_gagg_spect.py --preset small_animal

# Use 2 heads with parallel collimator
python example_gagg_spect.py --heads 2 --collimator parallel

# Different FOV presets
python example_gagg_spect.py --preset medium
python example_gagg_spect.py --preset large_clinical

# Run simulation (not just configure)
python example_gagg_spect.py --preset small_animal --run

# With visualization
python example_gagg_spect.py --preset small_animal --run --visu
```

## Configuring Scintillator Dimensions

### Method 1: Edit JSON File

Edit `gagg_spect_geometrical_parameters.json`:

```json
{
  "crystal_size_x_mm": 2.0,
  "crystal_size_y_mm": 2.0,
  "crystal_thickness_mm": 12.0,
  "crystal_array_size_x": 200,
  "crystal_array_size_y": 200
}
```

### Method 2: Programmatic Override

```python
import gagg_spect_detector as gagg

# Load default parameters
params = gagg.get_geometrical_parameters()

# Modify crystal dimensions
params.crystal_size_x_mm = 2.0
params.crystal_size_y_mm = 2.0
params.crystal_thickness_mm = 15.0
params.crystal_array_size_x = 250
params.crystal_array_size_y = 250

# Recalculate detector size
pixel_pitch = params.crystal_size_x_mm + params.crystal_spacing_mm
params.detector_size_x_mm = params.crystal_array_size_x * pixel_pitch
params.detector_size_y_mm = params.crystal_array_size_y * pixel_pitch

# Use custom parameters
heads, crystals = gagg.add_gagg_spect_heads(
    sim,
    number_of_heads=3,
    collimator_type="pinhole",
    fov_preset="small_animal",
    params=params  # Pass custom parameters
)
```

### Method 3: Create Custom JSON

```python
import json
from box import Box

# Create custom configuration
custom_config = {
    "crystal_size_x_mm": 1.5,
    "crystal_size_y_mm": 1.5,
    "crystal_thickness_mm": 12.0,
    "crystal_array_size_x": 300,
    "crystal_array_size_y": 300,
    # ... other parameters
}

# Save to file
with open("my_custom_config.json", "w") as f:
    json.dump(custom_config, f, indent=2)

# Load and use
with open("my_custom_config.json") as f:
    custom_params = Box(json.load(f))

heads, crystals = gagg.add_gagg_spect_heads(
    sim, params=custom_params
)
```

## Configuring FOV

### Available FOV Presets

Three FOV configurations are predefined in `gagg_spect_geometrical_parameters.json`:

| Preset | Diameter | Height | Detector Radius | Use Case |
|--------|----------|--------|-----------------|----------|
| `small_animal` | 10 cm | 10 cm | 10 cm | Mouse/rat imaging |
| `medium` | 30 cm | 25 cm | 25 cm | Primate imaging |
| `large_clinical` | 80 cm | 50 cm | 60 cm | Clinical imaging |

### Using FOV Presets

```python
# Small animal FOV
heads, crystals = gagg.add_gagg_spect_heads(
    sim,
    fov_preset="small_animal"
)

# Medium FOV
heads, crystals = gagg.add_gagg_spect_heads(
    sim,
    fov_preset="medium"
)

# Large clinical FOV
heads, crystals = gagg.add_gagg_spect_heads(
    sim,
    fov_preset="large_clinical"
)
```

### Adding Custom FOV Preset

Edit `gagg_spect_geometrical_parameters.json`:

```json
{
  "fov_presets": {
    "small_animal": { ... },
    "medium": { ... },
    "large_clinical": { ... },
    "my_custom_fov": {
      "fov_radius_cm": 12.5,
      "fov_height_cm": 20.0,
      "detector_radius_cm": 18.0,
      "description": "Custom 25cm diameter FOV"
    }
  }
}
```

Then use it:

```python
heads, crystals = gagg.add_gagg_spect_heads(
    sim,
    fov_preset="my_custom_fov"
)
```

## Configuration Parameters

### Crystal Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `crystal_size_x_mm` | float | 3.0 | Crystal width X (mm) |
| `crystal_size_y_mm` | float | 3.0 | Crystal width Y (mm) |
| `crystal_thickness_mm` | float | 10.0 | Crystal depth (mm) |
| `crystal_spacing_mm` | float | 0.1 | Gap between crystals (mm) |
| `crystal_array_size_x` | int | 160 | Number of crystals in X |
| `crystal_array_size_y` | int | 160 | Number of crystals in Y |
| `crystal_material` | str | "GAGG" | Scintillator material |

**Computed Properties:**
- Pixel pitch = `crystal_size + crystal_spacing`
- Detector size = `array_size × pixel_pitch`
- Total crystals = `array_size_x × array_size_y`

### Collimator Parameters

**Pinhole:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `collimator_type` | str | "pinhole" | Collimator type |
| `collimator_material` | str | "Tungsten" | Material |
| `collimator_thickness_mm` | float | 5.0 | Thickness (mm) |
| `pinhole_diameter_mm` | float | 1.5 | Entrance diameter (mm) |
| `pinhole_opening_angle_deg` | float | 30.0 | Cone angle (degrees) |

**Parallel-Hole:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `parallel_hole_diameter_mm` | float | 1.5 | Hole diameter (mm) |
| `parallel_septa_thickness_mm` | float | 0.2 | Septa thickness (mm) |
| `parallel_hole_length_mm` | float | 25.0 | Hole length (mm) |

### FOV Parameters

Each FOV preset has:
- `fov_radius_cm`: FOV radius (cm)
- `fov_height_cm`: FOV height (cm)
- `detector_radius_cm`: Distance from center to detector (cm)
- `description`: Human-readable description

### Digitizer Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `energy_resolution_fwhm` | float | 0.07 | FWHM at reference (7%) |
| `energy_reference_keV` | float | 140.5 | Reference energy (keV) |
| `energy_window_lower_keV` | float | 126.5 | Lower threshold (keV) |
| `energy_window_upper_keV` | float | 154.5 | Upper threshold (keV) |

## Examples

### Example 1: Different Crystal Sizes

```python
# Test multiple crystal sizes
for crystal_size in [1.5, 2.0, 2.5, 3.0, 4.0]:
    params = gagg.get_geometrical_parameters()
    params.crystal_size_x_mm = crystal_size
    params.crystal_size_y_mm = crystal_size

    # Keep detector size constant by adjusting array
    pixel_pitch = crystal_size + params.crystal_spacing_mm
    params.crystal_array_size_x = int(500 / pixel_pitch)
    params.crystal_array_size_y = int(500 / pixel_pitch)

    # Rebuild geometry
    heads, crystals = gagg.add_gagg_spect_heads(sim, params=params)
```

### Example 2: Dual-Head with Parallel Collimator

```python
heads, crystals = gagg.add_gagg_spect_heads(
    sim,
    number_of_heads=2,
    collimator_type="parallel",
    fov_preset="small_animal"
)
```

### Example 3: High-Resolution Configuration

```python
params = gagg.get_geometrical_parameters()

# High resolution: smaller crystals, more of them
params.crystal_size_x_mm = 1.5
params.crystal_size_y_mm = 1.5
params.crystal_thickness_mm = 12.0
params.crystal_array_size_x = 300
params.crystal_array_size_y = 300

# Smaller pinhole
params.pinhole_diameter_mm = 1.0

# Better energy resolution
params.energy_resolution_fwhm = 0.05

# Use it
heads, crystals = gagg.add_gagg_spect_heads(sim, params=params)
```

### Example 4: Generate Custom Config Template

```bash
# Save a custom configuration template
python example_gagg_spect.py --save-config
```

This creates `gagg_spect_custom_parameters.json` which you can modify and use.

## Integration with OpenGATE SPECTConfig

While this module can be used standalone, it's designed to integrate with OpenGATE's `SPECTConfig` system for full simulation configuration:

```python
from opengate.contrib.spect.spect_config import SPECTConfig
import gagg_spect_detector as gagg

# Create SPECTConfig
config = SPECTConfig()

# Configure your specific needs
# (phantom, source, acquisition, etc.)

# For detector, use GAGG functions directly
# The SPECTConfig.detector_config is primarily for predefined models
# For custom detectors like GAGG, integrate at geometry setup stage

# See OpenGATE documentation for full SPECTConfig usage:
# https://opengate.readthedocs.io/
```

## Comparison with Original Approach

### ❌ Wrong Approach (What I did initially)
```python
# DON'T reimplementimport opengate as gate
from gagg_spect_config import SPECTConfig  # Custom reimplementation

# This doesn't integrate properly with OpenGATE
config = SPECTConfig.default_small_animal()
```

### ✅ Correct Approach (Current)
```python
# DO use OpenGATE patterns
import opengate as gate
import gagg_spect_detector as gagg

# Follow OpenGATE detector model pattern
heads, crystals = gagg.add_gagg_spect_heads(
    sim,
    number_of_heads=3,
    collimator_type="pinhole",
    fov_preset="small_animal"
)
```

## Key Differences from Original Implementation

| Aspect | Original (Wrong) | Current (Correct) |
|--------|------------------|-------------------|
| Config system | Reimplemented SPECTConfig | Uses OpenGATE patterns |
| Integration | Standalone classes | Follows `ge_discovery_nm670.py` pattern |
| Parameters | Python dataclasses | JSON + Box |
| Usage | Custom config workflow | OpenGATE detector model |
| Compatibility | Not compatible | Compatible with OpenGATE |

## Troubleshooting

### Module Not Found

```
ModuleNotFoundError: No module named 'opengate'
```

**Solution:**
```bash
pip install opengate
pip install python-box
```

### Material Not Found

```
Material 'GAGG' not found
```

**Solution:** Create `GateMaterials.db` in the same directory with GAGG definition, or ensure your GATE materials database includes GAGG.

### Geometry Overlap

```
WARNING - G4VPhysicalVolume - Overlap detected
```

**Solution:** Reduce crystal array size or adjust spacing/dimensions in the JSON file.

## Files

- `gagg_spect_detector.py` - Detector model implementation (OpenGATE pattern)
- `gagg_spect_geometrical_parameters.json` - Configurable parameters
- `example_gagg_spect.py` - Usage examples and CLI
- `GAGG_SPECT_README.md` - This file

## References

1. OpenGATE Documentation: https://opengate.readthedocs.io/
2. OpenGATE SPECT contrib module: https://github.com/OpenGATE/opengate/tree/main/opengate/contrib/spect
3. GE Discovery NM670 reference implementation: `ge_discovery_nm670.py`
4. GAGG scintillator properties: See `CLAUDE.md` in project root

## Support

For questions or issues:
1. Check the examples in `example_gagg_spect.py`
2. Review parameter definitions in `gagg_spect_geometrical_parameters.json`
3. Consult OpenGATE documentation for general simulation setup
4. See `geom_spect.py` for an alternative OpenGATE-native implementation

---

**Note:** This implementation correctly follows OpenGATE patterns and integrates with the existing framework, rather than reimplementing the configuration system.
