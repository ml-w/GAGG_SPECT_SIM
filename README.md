# GAGG SPECT Pinhole Imaging System

## Overview

This project simulates a SPECT (Single Photon Emission Computed Tomography) imaging system using GAGG (Gd3Al2Ga3O12:Ce) scintillator crystals with pinhole collimation. The system is designed for nuclear medicine imaging with Tc-99m radioisotope.

## System Specifications

### Detector Configuration
- **Scintillator Material**: GAGG (Cerium-doped Gadolinium Aluminum Gallium Garnet)
- **Crystal Size**: 3 mm × 3 mm × 10 mm
- **Crystal Spacing**: 0.1 mm (inter-crystal gap)
- **Pixel Pitch**: 3.1 mm (crystal + gap)
- **Array Configuration**: 160 × 160 crystals per detector head
- **Total Detector Size**: ~50 cm × 50 cm per head
- **Number of Detector Heads**: 3 (arranged at 120° intervals)

### Collimator Design
- **Type**: Pinhole collimator
- **Material**: Tungsten
- **Collimator Thickness**: 5 mm
- **Pinhole Aperture**: Conical, 1.5-3 mm diameter
- **Purpose**: Provides magnification and spatial resolution

### Field of View (FOV)
- **Diameter**: 80 cm
- **Geometry**: Cylindrical water phantom (50 cm height)
- **Detector Radius**: 60 cm from center

### Source Configuration
- **Radioisotope**: Tc-99m (Technetium-99m)
- **Gamma Energy**: 140.5 keV (primary emission)
- **Number of Point Sources**: 3
- **Source Positions**:
  - Source 1: (0, 0, 0) cm - center
  - Source 2: (10, 0, 10) cm - diagonal offset
  - Source 3: (-10, 0, -10) cm - opposite diagonal
- **Activity per Source**: 1 MBq

## GAGG Scintillator Properties

GAGG is an advanced scintillator material with excellent properties for nuclear medicine imaging:

- **Light Yield**: ~26,000 photons/MeV
- **Decay Time**: ~40 ns (fast timing)
- **Emission Peak**: ~520 nm (green)
- **Energy Resolution**: ~7% at 140.5 keV
- **Density**: 6.63 g/cm³
- **Effective Z**: ~54 (high stopping power)
- **Advantages**: High light output, good energy resolution, non-hygroscopic

## File Structure

```
GAGG_SPECT/
├── README.md                    # This file
├── GATE_scripts/                # GATE macro files
│   ├── main.mac                 # Main simulation script
│   ├── geometry.mac             # Detector and collimator geometry
│   ├── physics.mac              # Physics processes and cuts
│   ├── digitizer.mac            # Digitizer chain (energy resolution, windows)
│   ├── source.mac               # Radiation source definitions
│   ├── output.mac               # Data output configuration
│   ├── verbose.mac              # Verbosity settings
│   └── visu.mac                 # Visualization settings
└── output/                      # Simulation output (created at runtime)
```

## Physics Configuration

### Electromagnetic Processes
- **Photoelectric Effect**: Standard model
- **Compton Scattering**: Standard model
- **Rayleigh Scattering**: Penelope model
- **Scintillation**: Enabled with optical photon tracking

### Energy Window
- **Photopeak Window**: 126.5-154.5 keV (20% window centered at 140.5 keV)
- **Purpose**: Accept photopeak events, reject scattered photons

### Production Cuts
- **World**: 1 mm (gamma, electron, positron)
- **Detector (crystal)**: 0.1 mm (improved accuracy in sensitive region)

## Running the Simulation

### Prerequisites
- GATE 9.4 with Geant4 11.2.1
- ROOT (for output analysis)
- Docker image: `opengatecollaboration/gate:9.4`

### Command-line Execution (Headless)

From the project root directory:

```bash
docker run -i --rm \
  -v $PWD:/APP \
  opengatecollaboration/gate:9.4 \
  Projects/GAGG_SPECT/GATE_scripts/main.mac
```

### Interactive Mode with Visualization

```bash
docker run -it --rm \
  -v $PWD:/APP \
  --volume="$HOME/.Xauthority:/root/.Xauthority:rw" \
  --net=host -e DISPLAY=$DISPLAY \
  opengatecollaboration/gate:9.4 \
  --qt Projects/GAGG_SPECT/GATE_scripts/main.mac
```

**Note**: Visualization requires X11 server on host (see main [CLAUDE.md](../../CLAUDE.md) for setup)

### Using the Project Script

Alternatively, from the repository root:

```bash
./run_gate.sh Projects/GAGG_SPECT/GATE_scripts/main.mac
```

## Output Files

After running the simulation, the following files are created in `output/`:

### ROOT Output
- **GAGG_SPECT.root**: Complete event data
  - Hits: Individual energy depositions in crystals
  - Singles: Processed events after digitizer chain

### Projection Output (Interfile format)
- **GAGG_SPECT_projection.hdr**: Header file with metadata
- **GAGG_SPECT_projection.sin**: Sinogram data (projection images)

### Analyzing Results

Use ROOT to inspect the data:

```bash
root -l output/GAGG_SPECT.root
```

Example ROOT commands:
```cpp
// View singles tree
Singles->Draw("energy")

// View hit positions
Hits->Draw("posX:posY")

// Energy spectrum
Singles->Draw("energy", "energy>100 && energy<200")
```

## Customization

### Modifying Source Positions

Edit [GATE_scripts/source.mac](GATE_scripts/source.mac):
```
/gate/source/source1/gps/centre X Y Z cm
```

### Changing Detector Configuration

Edit [GATE_scripts/geometry.mac](GATE_scripts/geometry.mac):
- Crystal size: `/gate/crystal/geometry/setX/Y/ZLength`
- Array size: `/gate/crystal/cubicArray/setRepeatNumber`
- Number of heads: `/gate/SPECThead/ring/setRepeatNumber`
- Detector radius: `/gate/SPECThead/placement/setTranslation`

### Adjusting Energy Windows

Edit [GATE_scripts/digitizer.mac](GATE_scripts/digitizer.mac):
```
/gate/digitizer/Singles/thresholder/setThreshold X keV
/gate/digitizer/Singles/upholder/setUphold Y keV
```

### Simulation Duration

Edit [GATE_scripts/main.mac](GATE_scripts/main.mac):
```
/gate/application/setTimeStop X s
```

## Typical Workflow

1. **Geometry Testing**: Run with visualization enabled to verify geometry
2. **Short Test Run**: Execute 1-second simulation to validate configuration
3. **Production Run**: Increase time to 60-600 seconds for adequate statistics
4. **Data Analysis**: Process ROOT output and projection data
5. **Image Reconstruction**: Use SPECT reconstruction algorithms (MLEM, OSEM) on projection data

## Design Rationale

### Three Detector Heads
- Provides 120° angular coverage
- Better angular sampling than dual-head systems
- Optimal for circular orbit SPECT

### Pinhole Collimation
- Enables magnification imaging
- Better sensitivity than parallel-hole for small FOV
- Suitable for small animal and dedicated organ imaging

### GAGG Scintillator
- Superior energy resolution vs. NaI(Tl) (7% vs. 10%)
- Faster decay time enables higher count rates
- Non-hygroscopic (easier handling than NaI)
- High density provides good stopping power at 140 keV

### 3 mm Crystal Size
- Balances spatial resolution and sensitivity
- Intrinsic resolution ~3 mm
- System resolution dominated by collimator for pinhole design

## References

- GATE Documentation: https://opengate.readthedocs.io/
- GAGG Properties: Kamada et al., J. Cryst. Growth 2012
- SPECT Physics: Cherry, Sorenson, Phelps - "Physics in Nuclear Medicine"

## Notes

- The simulation includes realistic physics (photoelectric, Compton, Rayleigh scattering)
- Energy blurring matches GAGG's 7% energy resolution at 140.5 keV
- Projection output is compatible with standard SPECT reconstruction tools
- For faster simulation, reduce crystal array size or simulation time
- Consider enabling dead time modeling for high count-rate studies
