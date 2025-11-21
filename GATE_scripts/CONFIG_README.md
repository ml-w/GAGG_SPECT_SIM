# GAGG SPECT Configurable Setup

## Overview

This configurable SPECT setup provides a flexible, Python-based configuration system for GAGG SPECT simulations using OpenGATE. It allows easy control of:

- **Scintillator dimensions** (crystal size, array configuration)
- **Field of View** (FOV radius, detector positioning)
- **Collimator type** (pinhole or parallel-hole)
- **Acquisition parameters** (duration, rotation, projections)
- **Source configuration** (isotope, energy, activity, geometry)
- **Digitizer settings** (energy resolution, windows, projection parameters)

## Architecture

The system is based on the OpenGATE `contrib/spect/spect_config.py` reference and consists of three main components:

### 1. Configuration Classes (`gagg_spect_config.py`)

Provides dataclass-based configuration with JSON serialization:

- `SPECTConfig` - Main configuration container
- `DetectorConfig` - Detector head configuration
- `ScintillatorConfig` - Crystal dimensions and array
- `CollimatorConfig` - Pinhole or parallel-hole collimator
- `FOVConfig` - Field of view and detector positioning
- `AcquisitionConfig` - Timing and rotation parameters
- `SourceConfig` - Radioactive source setup
- `DigitizerConfig` - Energy resolution and windowing

### 2. Geometry Builder (`gagg_spect_setup.py`)

Builds OpenGATE geometry from configuration:

- `create_simulation()` - Main entry point
- `add_detector_heads()` - Multi-head positioning
- `add_spect_head()` - Individual detector head
- `add_pinhole_collimator()` - Pinhole collimator
- `add_parallel_collimator()` - Parallel-hole collimator
- `add_digitizer()` - Digitizer chain setup

### 3. Example Scripts (`example_configurations.py`)

Pre-configured examples demonstrating various setups.

## Quick Start

### 1. Generate Example Configuration

```bash
# Show available examples
python example_configurations.py

# Generate small animal configuration
python example_configurations.py --example 1

# Generate all examples
python example_configurations.py --all
```

### 2. Run Simulation with Preset

```bash
# Run with default small animal preset
python gagg_spect_setup.py --preset small_animal

# Run with clinical preset
python gagg_spect_setup.py --preset clinical

# Enable visualization
python gagg_spect_setup.py --preset small_animal --visu --visu-type qt
```

### 3. Run with Custom Configuration

```bash
# Generate custom config
python example_configurations.py --example 2

# Run simulation with custom config
python gagg_spect_setup.py --config config_example2_highres.json
```

## Configuration Examples

### Example 1: Default Small Animal SPECT

```python
from gagg_spect_config import SPECTConfig
from gagg_spect_setup import create_simulation

# Use built-in preset
config = SPECTConfig.default_small_animal()

# Run simulation
sim = create_simulation(config)
sim.run()
```

**Configuration:**
- 3 detector heads (120° apart)
- 160×160 GAGG crystal array
- 3×3×10 mm³ crystals
- Pinhole collimator (1.5 mm)
- 10 cm FOV
- Tc-99m source
- 60-second acquisition

### Example 2: Custom Scintillator Dimensions

```python
from gagg_spect_config import SPECTConfig, ScintillatorConfig, DetectorConfig

# Custom configuration with different crystal size
config = SPECTConfig(
    name="CustomCrystalSize",
    detector=DetectorConfig(
        scintillator=ScintillatorConfig(
            crystal_size_x=2.0,       # 2mm crystals (instead of 3mm)
            crystal_size_y=2.0,
            crystal_thickness=12.0,   # 12mm thick (instead of 10mm)
            crystal_spacing=0.05,     # Tighter spacing
            array_size_x=200,         # More crystals
            array_size_y=200,
        )
    )
)

# Print summary
config.print_summary()

# Save to JSON
config.to_json("my_config.json")
```

### Example 3: Custom FOV

```python
from gagg_spect_config import SPECTConfig, FOVConfig

# Start with default
config = SPECTConfig.default_small_animal()

# Customize FOV
config.fov = FOVConfig(
    radius=7.5,              # 15 cm diameter
    height=15.0,
    detector_radius=15.0,
    name="custom_15cm"
)

# Run simulation
sim = create_simulation(config)
sim.run()
```

### Example 4: Parallel-Hole Collimator

```python
from gagg_spect_config import SPECTConfig, CollimatorConfig, DetectorConfig

config = SPECTConfig.default_small_animal()

# Change to parallel-hole collimator
config.detector.collimator = CollimatorConfig(
    type="parallel",
    material="Lead",
    parallel_hole_diameter=1.5,      # 1.5 mm holes
    parallel_septa_thickness=0.2,    # 0.2 mm septa
    parallel_hole_length=35.0,       # 35 mm length (LEHR)
)

sim = create_simulation(config)
sim.run()
```

### Example 5: Different Isotope (I-123)

```python
from gagg_spect_config import SPECTConfig, SourceConfig

config = SPECTConfig.default_small_animal()

# Change to I-123
config.source = SourceConfig(
    isotope="I123",
    energy=159.0,           # keV
    activity=5e6,           # 5 MBq
    geometry_type="sphere",
    geometry_radius=5.0,    # 5 mm sphere
)

# Adjust energy window
config.digitizer.energy_reference = 159.0
config.digitizer.energy_window_min = 143.0
config.digitizer.energy_window_max = 175.0

sim = create_simulation(config)
sim.run()
```

### Example 6: Load and Modify Configuration

```python
from gagg_spect_config import SPECTConfig

# Load existing configuration
config = SPECTConfig.from_json("config_example1_small_animal.json")

# Modify parameters
config.detector.scintillator.crystal_thickness = 15.0  # Thicker crystals
config.acquisition.duration = 120.0                     # Longer scan
config.source.activity = 2e6                            # Higher activity

# Save modified version
config.to_json("config_modified.json")

# Run simulation
sim = create_simulation(config)
sim.run()
```

## Configuration Parameters

### Scintillator Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `crystal_size_x` | float | 3.0 | Crystal width X (mm) |
| `crystal_size_y` | float | 3.0 | Crystal width Y (mm) |
| `crystal_thickness` | float | 10.0 | Crystal depth/thickness (mm) |
| `crystal_spacing` | float | 0.1 | Gap between crystals (mm) |
| `array_size_x` | int | 160 | Number of crystals in X |
| `array_size_y` | int | 160 | Number of crystals in Y |
| `material` | str | "GAGG" | Scintillator material |

**Computed properties:**
- `pixel_pitch_x/y` = crystal_size + crystal_spacing
- `detector_size_x/y` = array_size × pixel_pitch
- `total_crystals` = array_size_x × array_size_y

### FOV Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `radius` | float | 5.0 | FOV radius (cm) |
| `height` | float | 10.0 | FOV height (cm) |
| `detector_radius` | float | 10.0 | Detector distance from center (cm) |
| `name` | str | "small_fov" | Configuration name |

**Presets:**
- `FOVConfig.small_fov()` - 10 cm diameter (small animal)
- `FOVConfig.medium_fov()` - 30 cm diameter (primate)
- `FOVConfig.large_fov()` - 80 cm diameter (clinical)

### Collimator Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `type` | str | "pinhole" | "pinhole" or "parallel" |
| `material` | str | "Tungsten" | Collimator material |
| `thickness` | float | 5.0 | Collimator thickness (mm) |
| **Pinhole parameters:** | | | |
| `pinhole_diameter` | float | 1.5 | Entrance aperture (mm) |
| `pinhole_cone_angle` | float | 30.0 | Cone angle (degrees) |
| **Parallel parameters:** | | | |
| `parallel_hole_diameter` | float | 1.5 | Hole diameter (mm) |
| `parallel_septa_thickness` | float | 0.2 | Septa thickness (mm) |
| `parallel_hole_length` | float | 25.0 | Hole length (mm) |

### Detector Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `number_of_heads` | int | 3 | Number of detector heads (1-4) |
| `scintillator` | ScintillatorConfig | (default) | Scintillator configuration |
| `collimator` | CollimatorConfig | (default) | Collimator configuration |
| `shielding_material` | str | "Lead" | Shielding material |
| `shielding_thickness` | float | 5.0 | Shielding thickness (mm) |
| `backside_thickness` | float | 50.0 | PMT/electronics thickness (mm) |
| `backside_material` | str | "Glass" | Backing material |

**Head angles:**
- 1 head: [0°]
- 2 heads: [0°, 180°]
- 3 heads: [0°, 120°, 240°]
- 4 heads: [0°, 90°, 180°, 270°]

### Acquisition Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `duration` | float | 60.0 | Total acquisition time (s) |
| `rotation_enabled` | bool | True | Enable detector rotation |
| `rotation_speed` | float | 6.0 | Rotation speed (deg/s) |
| `number_of_projections` | int | 60 | Number of projections |

**Computed properties:**
- `time_per_projection` = duration / number_of_projections
- `angle_per_projection` = 360° / number_of_projections

### Source Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `isotope` | str | "Tc99m" | Isotope name |
| `energy` | float | 140.5 | Gamma energy (keV) |
| `activity` | float | 1e6 | Source activity (Bq) |
| `position` | tuple | (0,0,0) | Position (x,y,z) in mm |
| `geometry_type` | str | "point" | "point", "sphere", "cylinder" |
| `geometry_radius` | float | 1.0 | Radius for sphere/cylinder (mm) |
| `geometry_height` | float | 10.0 | Height for cylinder (mm) |

### Digitizer Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `energy_resolution` | float | 0.07 | FWHM at reference (7%) |
| `energy_reference` | float | 140.5 | Reference energy (keV) |
| `energy_window_min` | float | 126.5 | Lower threshold (keV) |
| `energy_window_max` | float | 154.5 | Upper threshold (keV) |
| `projection_size` | tuple | (160,160) | Projection image size (pixels) |
| `projection_spacing` | tuple | (3.1,3.1) | Pixel spacing (mm) |

## Output Files

Simulation creates the following output files (per detector head):

```
output/
├── hits_0.root              # Raw hit data (head 0)
├── hits_1.root              # Raw hit data (head 1)
├── hits_2.root              # Raw hit data (head 2)
├── projection_0.mhd         # Projection image (head 0)
├── projection_0.raw         # Projection data (head 0)
├── projection_1.mhd         # Projection image (head 1)
├── projection_1.raw         # Projection data (head 1)
├── projection_2.mhd         # Projection image (head 2)
└── projection_2.raw         # Projection data (head 2)
```

## Validation

All configurations are validated before simulation:

```python
config = SPECTConfig.default_small_animal()

if config.validate():
    print("✅ Configuration is valid")
    sim = create_simulation(config)
else:
    print("❌ Configuration has errors")
```

**Validation checks:**
- Number of heads (1-4)
- Positive crystal dimensions
- FOV detector radius > FOV radius
- Positive acquisition duration

## Advanced Usage

### Materials Database

Specify custom materials database:

```python
config = SPECTConfig.default_small_animal()
config.materials_database = "/path/to/Materials.xml"
```

The system automatically looks for `Materials.xml` in the script directory.

### Custom Physics List

```python
config = SPECTConfig.default_small_animal()
config.physics_list = "G4EmStandardPhysics_option3"
```

### Multiple Detector Heads

Test different head configurations:

```python
for n_heads in [1, 2, 3, 4]:
    config = SPECTConfig.default_small_animal()
    config.detector.number_of_heads = n_heads
    config.name = f"GAGG_SPECT_{n_heads}heads"
    print(f"Head angles: {config.detector.get_head_angles()}")
```

## Comparing with MAC Files

### Old Approach (MAC files)

```
/control/alias CRYSTAL_SIZE 3
/gate/crystal/geometry/setYLength {CRYSTAL_SIZE} mm
/gate/crystal/cubicArray/setRepeatNumberY 160
```

### New Approach (Python config)

```python
config = SPECTConfig(
    detector=DetectorConfig(
        scintillator=ScintillatorConfig(
            crystal_size_y=3.0,
            array_size_y=160,
        )
    )
)
```

**Advantages:**
- Type safety and validation
- Computed properties (e.g., detector_size)
- JSON serialization for reproducibility
- Easy parameter sweeps
- Reusable configurations
- Better documentation

## Parameter Sweep Example

Test multiple crystal sizes:

```python
from gagg_spect_config import SPECTConfig, ScintillatorConfig, DetectorConfig
from gagg_spect_setup import create_simulation

crystal_sizes = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0]

for size in crystal_sizes:
    config = SPECTConfig(
        name=f"GAGG_crystal_{size}mm",
        output_dir=f"output_crystal_{size}mm",
        detector=DetectorConfig(
            scintillator=ScintillatorConfig(
                crystal_size_x=size,
                crystal_size_y=size,
                array_size_x=int(500 / size),  # Keep ~500mm detector
                array_size_y=int(500 / size),
            )
        )
    )

    print(f"\nTesting {size}mm crystals...")
    config.print_summary()

    sim = create_simulation(config)
    sim.run()
```

## Troubleshooting

### Import Error

```
ModuleNotFoundError: No module named 'opengate'
```

**Solution:** Install OpenGATE:
```bash
pip install opengate
```

### Materials Not Found

```
⚠️  Material database not found
```

**Solution:**
1. Create `Materials.xml` in the same directory
2. Or specify path: `config.materials_database = "path/to/Materials.xml"`
3. Or use default GATE materials

### Overlap Error

```
WARNING - G4VPhysicalVolume - Overlap detected
```

**Solution:** Check collimator and crystal dimensions don't exceed head size

### Memory Error

```
Killed (out of memory)
```

**Solution:** Reduce array size or crystal count:
```python
config.detector.scintillator.array_size_x = 100  # Instead of 200
config.detector.scintillator.array_size_y = 100
```

## Performance Tips

1. **Start small:** Test with reduced array size first
2. **Use presets:** Start with `default_small_animal()` or `default_clinical()`
3. **Disable visualization:** For production runs, don't use `--visu`
4. **Reduce simulation time:** Test with short duration first
5. **JSON configs:** Save successful configs for reuse

## References

1. OpenGATE Documentation: https://opengate.readthedocs.io/
2. OpenGATE SPECT Config Reference:
   https://github.com/OpenGATE/opengate/blob/10.0.3/opengate/contrib/spect/spect_config.py
3. GAGG Scintillator Properties: See `CLAUDE.md`
4. SPECT Physics: Cherry, Sorenson, Phelps - "Physics in Nuclear Medicine"

## Support

For issues or questions:
1. Check example configurations: `python example_configurations.py`
2. Validate configuration: `config.validate()`
3. Review parameter ranges in this README
4. Check GATE documentation for physics/geometry details
