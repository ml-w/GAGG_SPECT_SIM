# OpenGATE SPECT Examples

This directory contains examples demonstrating how to reuse the OpenGATE SPECT contribution code (`opengate.contrib.spect`) for SPECT simulations.

## Overview

The examples show two approaches to creating SPECT simulations:

1. **`example_opengate_spect.py`** - Direct API usage with detailed control
2. **`example_spect_config.py`** - High-level SPECTConfig class for comprehensive configuration

Both examples are fully configurable for:
- ✅ Field of View (FOV)
- ✅ Crystal type (GE NM670 or Siemens Intevo)
- ✅ SPECT head dimensions and readout resolution
- ✅ Simple point sources

## Installation

### Prerequisites

- Python 3.8+
- pip

### Install OpenGATE

The OpenGATE package includes the SPECT contribution modules we'll be using:

```bash
# Install from PyPI (recommended)
pip install opengate

# Or install from GitHub (latest development version)
pip install git+https://github.com/OpenGATE/opengate.git
```

### Install Additional Dependencies

```bash
pip install numpy itk SimpleITK
```

## Quick Start

### Example 1: Direct API Usage

This example demonstrates direct usage of the detector-specific functions:

```bash
python example_opengate_spect.py
```

**Key features:**
- Configurable detector model (GE NM670 or Siemens Intevo)
- Multiple detector heads with custom positioning
- Digitizer chain with energy and spatial blurring
- Simple point source configuration
- Configurable FOV and pixel resolution

**Configuration parameters** (edit in `SPECTSimulationConfig` class):

```python
# System configuration
self.detector_model = "GE_NM670"  # or "SIEMENS_INTEVO"
self.crystal_size = "3/8"  # or "5/8" (for GE only)
self.collimator_type = "lehr"  # or "megp", "hegp"

# Field of View
self.fov_size = [40, 40, 40]  # cm [x, y, z]

# Readout resolution
self.pixel_size = [0.35, 0.35]  # cm [x, y]

# SPECT heads
self.num_heads = 2
self.detector_radius = 36  # cm
self.head_angles = [0, 180]  # degrees

# Source
self.source_position = [0, 0, 0]  # cm
self.source_activity = 1e6  # Bq
```

### Example 2: SPECTConfig Class

This example uses the high-level configuration API:

```bash
python example_spect_config.py
```

**Key features:**
- Comprehensive configuration through config objects
- Detector, phantom, source, and acquisition configuration
- Serialization support (save/load from JSON)
- Voxelized phantom and activity distribution support

**Configuration structure:**

```python
config = spect_config.SPECTConfig()

# Detector
config.detector = spect_config.DetectorConfig()
config.detector.model = "Intevo"  # or "NM670"
config.detector.collimator = "lehr"
config.detector.number_of_heads = 2
config.detector.energy_resolution = 0.07
config.detector.spatial_blur_fwhm = 0.35  # cm (pixel size)

# Acquisition
config.acquisition = spect_config.AcquisitionConfig()
config.acquisition.radius = 36  # cm
config.acquisition.number_of_projections = 60
config.acquisition.duration = 20  # seconds

# Phantom (FOV)
config.phantom = spect_config.PhantomConfig()
config.phantom.voxel_size = [0.4, 0.4, 0.4]  # cm

# Source
config.source = spect_config.SourceConfig()
config.source.isotope = "Tc99m"
config.source.total_activity = 1e6  # Bq
```

## Configuration Options

### Detector Models

#### GE Discovery NM670
- Crystal sizes: `"3/8"` (9.525mm) or `"5/8"` (15.875mm)
- Crystal dimensions: 54 × 40 cm
- Collimators: `"lehr"`, `"megp"`, `"hegp"`

#### Siemens Intevo
- Crystal: 9.5mm NaI
- Crystal dimensions: 53.3 × 38.7 cm
- Collimators: `"lehr"`, `"melp"`, `"he"`

### Collimator Types

| Type | Full Name | Hole Size | Isotope |
|------|-----------|-----------|---------|
| LEHR | Low Energy High Resolution | 1.11-1.5mm | Tc-99m |
| MEGP/MELP | Medium Energy General/Low Penetration | 2.94-3mm | In-111, Lu-177 |
| HEGP/HE | High Energy General Purpose | 4mm | I-131 |

### Field of View Configuration

Control the imaging region through:

**Example 1 (Direct API):**
```python
config.fov_size = [40, 40, 40]  # cm
config.pixel_size = [0.35, 0.35]  # cm
```

**Example 2 (SPECTConfig):**
```python
config.phantom.size = [100, 100, 100]  # voxels
config.phantom.voxel_size = [0.4, 0.4, 0.4]  # cm
# FOV = size × voxel_size = 40×40×40 cm
```

### Crystal Type and Readout Resolution

The detector crystal and readout resolution affect:
- **Energy resolution**: Set via `energy_resolution` (e.g., 0.07 = 7%)
- **Spatial resolution**: Set via `pixel_size` or `spatial_blur_fwhm` (cm)

**Example:**
```python
# For GAGG-like performance
detector.energy_resolution = 0.07  # 7% @ 140.5 keV
detector.spatial_blur_fwhm = 0.35  # cm (3.5mm pixels)

# For NaI-like performance
detector.energy_resolution = 0.10  # 10% @ 140.5 keV
detector.spatial_blur_fwhm = 0.45  # cm (4.5mm pixels)
```

## Output

Both examples generate:
- **ROOT files**: Raw hits and singles data
- **MHD/RAW files**: Projection images (2D)
- **Statistics**: Event counts and timing

Output location: `./output_opengate_spect/` or `./output_spect_config/`

## Advanced Usage

### Save/Load Configuration

```python
# Save configuration
config.to_json("my_spect_config.json")

# Load configuration
loaded_config = spect_config.SPECTConfig.from_json("my_spect_config.json")
```

### Custom Activity Distribution

```python
# Create custom activity distribution
activity = np.zeros((100, 100, 100))
# Define hot spot
activity[40:60, 40:60, 45:55] = 1.0

# Normalize and assign
activity = activity / np.sum(activity)
config.source.activity_distribution = activity
```

### Multiple Detector Heads

```python
# Example 1: Configure head angles
config.num_heads = 3
config.head_angles = [0, 120, 240]  # 120° spacing

# Example 2: SPECTConfig
config.detector.number_of_heads = 3
```

## OpenGATE SPECT Contribution Module

The examples reuse code from:
- **Repository**: https://github.com/OpenGATE/opengate
- **Module**: `opengate/contrib/spect/`

### Key Components

1. **`spect_config.py`**: High-level configuration classes
   - `SPECTConfig`: Main orchestrator
   - `DetectorConfig`: Detector specifications
   - `PhantomConfig`: Voxelized phantom setup
   - `SourceConfig`: Activity distribution
   - `AcquisitionConfig`: Gantry motion and timing

2. **`ge_discovery_nm670.py`**: GE scanner implementation
   - `add_spect_head()`: Create detector head
   - `add_spect_two_heads()`: Dual-head configuration

3. **`siemens_intevo.py`**: Siemens scanner implementation
   - `add_spect_head()`: Create detector head
   - `rotate_gantry()`: Configure rotation

4. **`spect_helpers.py`**: Utility functions
   - Image processing
   - Uncertainty calculations
   - Collimator physics

## Troubleshooting

### ImportError: No module named 'opengate'

```bash
pip install opengate
```

### GATE/Geant4 Not Found

OpenGATE includes Geant4 bindings. Ensure you have a compatible Python version (3.8+).

### Memory Issues

Reduce the simulation parameters:
```python
config.acquisition.number_of_projections = 30  # Reduce projections
config.acquisition.duration = 10  # Reduce duration
config.source.total_activity = 1e5  # Reduce activity
```

### Slow Simulations

Increase parallelization:
```python
config.number_of_threads = 8  # Use more threads
```

## Comparison with Local GATE Scripts

### Old Approach (Local .mac files)
- ❌ Manual material definitions
- ❌ Hardcoded geometry
- ❌ No reusability
- ❌ Difficult to configure

### New Approach (OpenGATE Contrib)
- ✅ Validated detector models
- ✅ Material databases included
- ✅ High-level configuration API
- ✅ Easy customization
- ✅ Community-maintained

## References

- **OpenGATE Documentation**: http://opengate.readthedocs.io/
- **OpenGATE GitHub**: https://github.com/OpenGATE/opengate
- **GATE Homepage**: http://www.opengatecollaboration.org/

## License

These examples follow the OpenGATE license (Apache 2.0).

## Contributing

Improvements and additional examples are welcome! Submit issues or pull requests to the main GAGG_SPECT_SIM repository.
