# CLAUDE.md - GAGG SPECT Simulation Project

## Project Overview

This is an **OpenGATE Python** Monte Carlo simulation for a SPECT (Single Photon Emission Computed Tomography) imaging system using GAGG (Gd₃Al₂Ga₃O₁₂:Ce) scintillator crystals with pinhole collimation, designed for Tc-99m (140.5 keV) imaging.

**IMPORTANT**: This project uses the **OpenGATE Python package** (opengate), not the legacy macro-based GATE. All simulations are defined programmatically in Python.

## Task: GAGG Material Specifications

### Chemical Formula
**Gd₃Al₂Ga₃O₁₂:Ce** (Cerium-doped Gadolinium Aluminum Gallium Garnet)

### Physical Properties

| Property | Value | Notes |
|----------|-------|-------|
| Density | 6.63 g/cm³ | Theoretical density |
| Effective Atomic Number (Zeff) | 54.4 | High stopping power for gamma rays |
| Melting Point | 1850°C | |
| Hardness | 8 Mohs | Very hard, durable |
| Cleavage Plane | None | Mechanically robust |
| Hygroscopic | No | No special handling required |
| Crystal Structure | Garnet (cubic) | |

### Optical Properties

| Property | Value | Notes |
|----------|-------|-------|
| Emission Peak Wavelength | 520 nm | Green emission, matches SiPM/PMT sensitivity |
| Emission Wavelength Range | 475–800 nm | |
| Refractive Index | 1.9 @ 540 nm | |

### Scintillation Properties

| Property | Value | Notes |
|----------|-------|-------|
| Light Yield | 40,000–60,000 photons/MeV | Grade dependent |
| Typical Light Yield | ~46,000–50,000 photons/MeV | Standard grade |
| Decay Time | 50–150 ns | Grade dependent |
| Typical Decay Time | ~90 ns | Balanced grade |
| Energy Resolution | ~4.9% @ 662 keV | For optimized samples |

### GAGG Grades Available

| Grade | Light Yield | Decay Time | Use Case |
|-------|-------------|------------|----------|
| High Light Yield | 60,000 ph/MeV | <150 ns | Maximum sensitivity |
| Balanced | 50,000 ph/MeV | <90 ns | General purpose SPECT/PET |
| Fast Decay | 40,000 ph/MeV | <50 ns | High count rate, TOF-PET |

### Elemental Composition

For GATE material definition, the atomic composition of Gd₃Al₂Ga₃O₁₂:

| Element | Symbol | Atomic Number | Atoms per Formula Unit | Mass Fraction |
|---------|--------|---------------|------------------------|---------------|
| Gadolinium | Gd | 64 | 3 | ~59.4% |
| Aluminum | Al | 13 | 2 | ~6.8% |
| Gallium | Ga | 31 | 3 | ~26.3% |
| Oxygen | O | 8 | 12 | ~7.5% |

*Note: Ce dopant is typically <1% and can be ignored for simulation purposes*

### Comparison with Other Scintillators

| Property | GAGG:Ce | LYSO:Ce | NaI(Tl) | BGO |
|----------|---------|---------|---------|-----|
| Density (g/cm³) | 6.63 | 7.1 | 3.67 | 7.13 |
| Zeff | 54.4 | 66 | 51 | 75 |
| Light Yield (ph/MeV) | 46,000 | 30,000 | 38,000 | 8,200 |
| Decay Time (ns) | 90 | 40 | 230 | 300 |
| Hygroscopic | No | No | Yes | No |
| Emission Peak (nm) | 520 | 420 | 415 | 480 |

### Advantages of GAGG for SPECT

1. **High light yield** - Excellent energy resolution for photopeak discrimination
2. **Non-hygroscopic** - No hermetic sealing required, simplified detector assembly
3. **High Zeff** - Good photoelectric absorption efficiency at 140 keV
4. **Green emission** - Well-matched to SiPM peak sensitivity (~520 nm)
5. **Mechanically robust** - No cleavage, high hardness
6. **Non-self-radioactive** - Unlike LYSO (contains Lu-176)

### References

1. Advatech UK - GAGG(Ce) Scintillator Crystal
   - https://www.advatech-uk.co.uk/gagg_ce.html

2. Shalomeo - GAGG(Ce) Scintillator Crystals
   - https://www.shalomeo.com/Scintillators/GAGG-Ce/product-394.html

3. Crylink - Ce:GAGG Scintillator Crystals
   - https://www.scintillator-crylink.com/

4. Epic Crystal - GAGG Scintillator
   - http://www.epic-scintillator.com/

5. ScienceDirect - Scintillation properties of Gd3Al2Ga3O12:Ce
   - https://www.sciencedirect.com/science/article/abs/pii/S0925346718301691

---

## Project Structure

```
GAGG_SPECT_SIM/
├── README.md                                    # Project documentation
├── CLAUDE.md                                    # This file - task specifications
├── requirements.txt                             # Python dependencies
└── GATE_scripts/
    ├── quick_start.py                           # Quick start example (minimal setup)
    ├── example_gagg_spect.py                    # Comprehensive examples with CLI
    ├── gagg_spect_detector.py                   # GAGG detector model module
    ├── gagg_spect_geometrical_parameters.json   # Detector configuration
    ├── geom_spect.py                            # Geometry utilities
    ├── visualize_only.py                        # Visualization script
    ├── convert_mhd_to_png.py                    # Output conversion utility
    └── *.mac                                    # Legacy macro files (reference only)
```

## Installation

### Prerequisites

- Python 3.8 or higher
- OpenGATE Python package (opengate >= 10.0)

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd GAGG_SPECT_SIM

# Install dependencies
pip install -r requirements.txt

# Or install individually
pip install opengate numpy scipy python-box matplotlib
```

### Verify Installation

```bash
cd GATE_scripts
python gagg_spect_detector.py
```

This should display the detector configuration parameters.

## Key Simulation Parameters

- **Scintillator**: GAGG crystals (3mm × 3mm × 10mm)
- **Crystal array**: 160 × 160 per head
- **Detector heads**: 1-4 configurable (default: 3 at 120° spacing)
- **Collimator**: Tungsten pinhole (1.5mm aperture) or parallel-hole
- **Source**: Tc-99m (140.5 keV) - configurable
- **Energy resolution**: 7% FWHM @ 140.5 keV
- **Energy window**: 126.5–154.5 keV (±10%)

## Quick Start

The fastest way to get started is with `quick_start.py`:

```bash
cd GATE_scripts
python quick_start.py
```

This creates a minimal 3-head GAGG SPECT system with:
- 3 detector heads at 120° spacing
- Pinhole collimation
- Small animal FOV (10 cm diameter)
- Tc-99m point source at center
- 1 second simulation time

## Usage Examples

### 1. Quick Start (Minimal Configuration)

```python
import opengate as gate
import gagg_spect_detector as gagg

# Create simulation
sim = gate.Simulation()
sim.world.size = [100 * gate.g4_units.cm] * 3
sim.world.material = "G4_AIR"

# Add GAGG detector heads
heads, crystals = gagg.add_gagg_spect_heads(
    sim,
    number_of_heads=3,
    collimator_type="pinhole",
    fov_preset="small_animal"
)

# Add digitizer for each head
for i, crystal in enumerate(crystals):
    gagg.add_gagg_digitizer(sim, crystal.name, name=f"head_{i}")

# Add Tc-99m point source
source = sim.add_source("GenericSource", "tc99m")
source.particle = "gamma"
source.energy.mono = 140.5 * gate.g4_units.keV
source.activity = 1e6 * gate.g4_units.Bq  # 1 MBq
source.position.type = "point"
source.direction.type = "iso"

# Physics
sim.physics_manager.physics_list_name = "G4EmStandardPhysics_option4"

# Run for 1 second
sim.run_timing_intervals = [[0, 1 * gate.g4_units.second]]
sim.run()
```

### 2. Comprehensive Examples with CLI

For more examples, use `example_gagg_spect.py`:

```bash
# Run with visualization
python example_gagg_spect.py --preset small_animal --run --visu

# Different configurations
python example_gagg_spect.py --preset medium --heads 2 --collimator parallel --run

# Large clinical FOV
python example_gagg_spect.py --preset large_clinical --heads 4 --run

# Save custom configuration template
python example_gagg_spect.py --save-config
```

### 3. Custom Crystal Dimensions

```python
import opengate as gate
import gagg_spect_detector as gagg

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

# Create simulation with custom parameters
sim = gate.Simulation()
heads, crystals = gagg.add_gagg_spect_heads(
    sim,
    number_of_heads=3,
    collimator_type="pinhole",
    fov_preset="small_animal",
    params=params  # Pass custom parameters
)
```

## FOV Presets

The simulation supports three field-of-view configurations:

| Preset | FOV Diameter | FOV Height | Detector Radius | Application |
|--------|--------------|------------|-----------------|-------------|
| `small_animal` | 10 cm | 10 cm | 10 cm | Mouse, rat imaging |
| `medium` | 30 cm | 25 cm | 25 cm | Rabbit, primate imaging |
| `large_clinical` | 80 cm | 50 cm | 60 cm | Human clinical imaging |

## Collimator Types

### Pinhole Collimator (Default)
- **Aperture**: 1.5 mm diameter
- **Opening angle**: 30°
- **Thickness**: 5 mm tungsten
- **Use case**: High magnification, small FOV imaging

### Parallel-Hole Collimator
- **Hole diameter**: 1.5 mm
- **Septa thickness**: 0.2 mm
- **Hole length**: 25 mm
- **Pattern**: Hexagonal close-packed
- **Use case**: General purpose SPECT imaging

## Configuration File

All detector parameters are defined in `gagg_spect_geometrical_parameters.json`:

- Crystal dimensions and array size
- Collimator specifications
- FOV presets
- Energy resolution and windows
- Material definitions

You can create custom configurations by copying and modifying this file, then loading it with:

```python
import json
from box import Box

with open("my_custom_config.json") as f:
    custom_params = Box(json.load(f))

gagg.add_gagg_spect_heads(sim, params=custom_params)
```

## Output Files

OpenGATE simulations produce:

### 1. Hits ROOT Files
- **Format**: ROOT tree with individual energy depositions
- **Location**: `output/<name>_hits.root`
- **Contains**: Position, energy, time, volume ID for each hit

### 2. Projection Images
- **Format**: MetaImage (MHD/RAW)
- **Location**: `output/<name>_projection.mhd` + `.raw`
- **Contains**: 2D projection images for each detector head
- **Resolution**: Matches crystal array (default 160×160)

### 3. Converting Projections

Use the conversion utility:

```bash
python convert_mhd_to_png.py output/head_0_projection.mhd
```

## Physics Configuration

The simulation uses:
- **Physics list**: `G4EmStandardPhysics_option4` (accurate EM physics)
- **Processes**: Photoelectric effect, Compton scattering, Rayleigh scattering
- **Production cuts**: 0.1 mm in detector, 1 mm elsewhere
- **Optical photons**: Can be enabled for detailed scintillation modeling

## Digitizer Chain

Each detector head includes:

1. **Hits Collection**: Record all energy depositions in crystals
2. **Adder**: Sum energy deposits per crystal (Singles)
3. **Energy Blurring**: Apply detector resolution (7% FWHM @ 140.5 keV)
4. **Energy Window**: Accept photopeak events (126.5-154.5 keV)
5. **Projection**: Create 2D images matching detector geometry

## Common Tasks

### Visualize Geometry

```python
sim.visu = True
sim.visu_type = "qt"
sim.run()
```

Or use the dedicated script:

```bash
python visualize_only.py
```

### Change Source Activity

```python
source.activity = 10e6 * gate.g4_units.Bq  # 10 MBq
```

### Change Simulation Time

```python
sim.run_timing_intervals = [[0, 60 * gate.g4_units.second]]  # 60 seconds
```

### Multiple Sources

```python
# Source 1
source1 = sim.add_source("GenericSource", "source1")
source1.particle = "gamma"
source1.energy.mono = 140.5 * gate.g4_units.keV
source1.activity = 1e6 * gate.g4_units.Bq
source1.position.translation = [0, 0, 10 * gate.g4_units.mm]

# Source 2
source2 = sim.add_source("GenericSource", "source2")
source2.particle = "gamma"
source2.energy.mono = 140.5 * gate.g4_units.keV
source2.activity = 1e6 * gate.g4_units.Bq
source2.position.translation = [0, 0, -10 * gate.g4_units.mm]
```

## Debug Mode

For faster testing during development:

```python
heads, crystals = gagg.add_gagg_spect_heads(
    sim,
    number_of_heads=1,  # Single head
    debug=True  # Reduced crystal array (20×20 instead of 160×160)
)
```
