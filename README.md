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
Two switchable FOV configurations are available:

**Large FOV (80 cm diameter)** - Default
- **Radius**: 40 cm
- **Height**: 50 cm
- **Detector Radius**: 60 cm from center
- **Use case**: Standard clinical imaging

**Small FOV (10 cm diameter)**
- **Radius**: 5 cm
- **Height**: 10 cm
- **Detector Radius**: 10 cm from center
- **Use case**: Small animal or high-resolution imaging

To switch FOV, edit `geometry.mac` and uncomment the desired configuration.

### Detector Rotation
- **Rotation axis**: Y-axis (vertical)
- **Speed**: Configurable (default: 0 deg/s = static)
- **Examples**: 6 deg/s = 60s full rotation, 1 deg/s = 360s full rotation
- **Use case**: SPECT tomographic acquisition

### Source Configuration

#### Configurable Tracers
The following radioisotopes are supported (edit `source.mac` to change):

| Tracer | Energy (keV) | Application |
|--------|--------------|-------------|
| **Tc-99m** | 140.5 | General SPECT (default) |
| I-123 | 159.0 | Thyroid imaging |
| I-131 | 364.0 | Thyroid therapy |
| Tl-201 | 71.0 | Cardiac imaging |
| In-111 | 171.0 | Infection imaging |

#### Point Sources (Resolution Test Pattern)
7 point sources arranged along Z-axis with increasing spacing:

| Source | Position (mm) | Spacing (mm) |
|--------|---------------|--------------|
| 1 | 0 | - |
| 2 | 1 | 1 |
| 3 | 3 | 2 |
| 4 | 6 | 3 |
| 5 | 10 | 4 |
| 6 | 15 | 5 |
| 7 | 21 | 6 |

- **Activity per Source**: 1 MBq (configurable)

#### Ring Sources (Resolution Test)
24 ring sources for testing resolution at different diameters:

| Diameter (mm) | Orientations | Center Position |
|---------------|--------------|-----------------|
| 0.1 | X, Y, Z | (0, 30, 0) mm |
| 0.5 | X, Y, Z | (0, 30, 0) mm |
| 1 | X, Y, Z | (0, 30, 0) mm |
| 2 | X, Y, Z | (0, 30, 0) mm |
| 3 | X, Y, Z | (0, 30, 0) mm |
| 4 | X, Y, Z | (0, 30, 0) mm |
| 5 | X, Y, Z | (0, 30, 0) mm |
| 6 | X, Y, Z | (0, 30, 0) mm |

- Each size has 3 rings aligned with X, Y, Z axes
- Total: 24 ring sources
- Ring orientations: X-aligned (YZ plane), Y-aligned (XZ plane), Z-aligned (XY plane)

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

### Starting the Simulation

#### Step 1: Configure the Simulation

Before running, review and modify these configuration files as needed:

1. **Tracer Selection** (`source.mac`):
   - Uncomment the desired tracer energy alias (default: Tc-99m)

2. **FOV Selection** (`geometry.mac`):
   - Uncomment either Large FOV (80cm) or Small FOV (10cm) configuration

3. **Detector Rotation** (`geometry.mac`):
   - Set `ROTATION_SPEED` alias (0 = static, 6 = one rotation per minute)

4. **Simulation Duration** (`main.mac`):
   - Modify `/gate/application/setTimeStop` (default: 1 s)

#### Step 2: Run the Simulation

**Command-line Execution (Headless/Production)**

From the project root directory:

```bash
docker run -i --rm \
  -v $PWD:/APP \
  opengatecollaboration/gate:9.4 \
  Projects/GAGG_SPECT/GATE_scripts/main.mac
```

**Using the Project Script**

Alternatively, from the repository root:

```bash
./run_gate.sh Projects/GAGG_SPECT/GATE_scripts/main.mac
```

## Visualizing the Scene

### Method 1: Interactive OpenGL Visualization

To visualize the geometry and particle tracks in real-time:

1. **Enable visualization** in `main.mac` by uncommenting:
   ```
   /control/execute visu.mac
   ```

2. **Run with Qt interface**:
   ```bash
   docker run -it --rm \
     -v $PWD:/APP \
     --volume="$HOME/.Xauthority:/root/.Xauthority:rw" \
     --net=host -e DISPLAY=$DISPLAY \
     opengatecollaboration/gate:9.4 \
     --qt Projects/GAGG_SPECT/GATE_scripts/main.mac
   ```

3. **Visualization controls** (in Qt viewer):
   - Rotate: Left mouse button + drag
   - Zoom: Scroll wheel or right mouse button + drag
   - Pan: Middle mouse button + drag
   - View preset: `/vis/viewer/set/viewpointThetaPhi 70 20`

**Note**: Requires X11 server on host. On Linux, run `xhost +local:docker` first.

### Method 2: Export to VRML/GDML for External Viewers

Add to `visu.mac` for file export:

```
# Export to VRML (viewable in many 3D viewers)
/vis/open VRML2FILE
/vis/drawVolume
/vis/viewer/flush

# Export to GDML (Geant4 geometry format)
/gate/geometry/export geometry.gdml
```

### Visualization Settings

The `visu.mac` file configures:
- **Window size**: 600x600 pixels
- **Viewing angle**: theta=70°, phi=20°
- **Zoom**: 1.5x
- **Style**: Wireframe (can change to `surface`)
- **Trajectories**: Particle tracks are displayed
- **Axes**: 10 cm coordinate axes at origin

### What You'll See

- **White boxes**: SPECT detector heads (3 at 120° intervals)
- **Grey solid**: Tungsten collimator with blue pinhole
- **Green blocks**: GAGG crystal array
- **Cyan wireframe**: FOV water phantom cylinder
- **Colored tracks**: Gamma rays (green), electrons (red)
- **Axes**: X (red), Y (green), Z (blue)

## Output Files

After running the simulation, the following files are created in `output/`:

### ROOT Output
- **GAGG_SPECT.root**: Complete event data
  - Hits: Individual energy depositions in crystals
  - Singles: Processed events after digitizer chain

### Projection Output (Interfile format)
- **GAGG_SPECT_projection.hdr**: Header file with metadata
- **GAGG_SPECT_projection.sin**: Sinogram data (projection images)

## Collecting Sinogram Data

### What is a Sinogram?

A sinogram is a 2D representation of projection data acquired at multiple angles around the object. In SPECT imaging, sinograms are used for tomographic image reconstruction.

### Sinogram Configuration

The sinogram output is configured in `output.mac`:

```bash
/gate/output/projection/enable
/gate/output/projection/setFileName ../output/GAGG_SPECT_projection
/gate/output/projection/pixelSizeX 3.1 mm      # Matches detector pixel pitch
/gate/output/projection/pixelSizeY 3.1 mm
/gate/output/projection/pixelNumberX 160       # Matches detector array size
/gate/output/projection/pixelNumberY 160
/gate/output/projection/projectionPlane YZ     # Projection plane orientation
```

### Acquiring Sinogram Data

#### For Static Acquisition (Single Projection)

1. Set `ROTATION_SPEED 0` in `geometry.mac`
2. Run simulation for desired duration
3. Output: Single projection image

#### For Tomographic Acquisition (Multiple Projections)

1. **Enable detector rotation** in `geometry.mac`:
   ```
   /control/alias ROTATION_SPEED 6
   ```
   This gives 6°/s rotation = 60 projections in 60 seconds (1° steps)

2. **Configure time slices** in `main.mac`:
   ```bash
   /gate/application/setTimeSlice 1 s      # Time per projection
   /gate/application/setTimeStart 0 s
   /gate/application/setTimeStop 60 s      # Total acquisition time
   ```

3. **Run the simulation**:
   - This produces 60 projection images (one per second)
   - Each image corresponds to a different detector angle

### Sinogram File Format

#### Interfile Header (`.hdr`)

The header file contains metadata about the sinogram:

```
!INTERFILE :=
!imaging modality := nucmed
!version of keys := 3.3
!name of data file := GAGG_SPECT_projection.sin
!matrix size [1] := 160
!matrix size [2] := 160
!number of projections := 60
!extent of rotation := 360
!process status := acquired
```

#### Binary Data (`.sin`)

The sinogram data is stored as:
- Format: 32-bit float (little-endian)
- Dimensions: [number_of_projections] × [pixelNumberY] × [pixelNumberX]
- Order: Projection-major (all pixels for projection 0, then projection 1, etc.)

### Reading Sinogram Data

#### Using Python

```python
import numpy as np

# Read binary sinogram data
n_projections = 60
n_pixels_y = 160
n_pixels_x = 160

sinogram = np.fromfile('output/GAGG_SPECT_projection.sin', dtype=np.float32)
sinogram = sinogram.reshape((n_projections, n_pixels_y, n_pixels_x))

# Display a single projection
import matplotlib.pyplot as plt
plt.imshow(sinogram[0], cmap='hot')
plt.colorbar(label='Counts')
plt.title('Projection at 0°')
plt.show()

# Display sinogram (single slice)
slice_idx = 80  # Middle slice
sino_slice = sinogram[:, slice_idx, :]
plt.imshow(sino_slice, aspect='auto', cmap='hot')
plt.xlabel('Detector bin')
plt.ylabel('Projection angle')
plt.title(f'Sinogram (slice {slice_idx})')
plt.show()
```

#### Using MATLAB

```matlab
% Read sinogram
fid = fopen('output/GAGG_SPECT_projection.sin', 'rb');
sinogram = fread(fid, [160*160*60], 'float32');
fclose(fid);

% Reshape
sinogram = reshape(sinogram, [160, 160, 60]);
sinogram = permute(sinogram, [3, 2, 1]);  % [projections, y, x]

% Display
imagesc(squeeze(sinogram(1, :, :)));
colorbar;
title('Projection at 0°');
```

### Image Reconstruction

Sinograms can be reconstructed using standard SPECT algorithms:

1. **Filtered Back-Projection (FBP)**: Fast, analytical method
2. **MLEM (Maximum Likelihood Expectation Maximization)**: Iterative, better noise handling
3. **OSEM (Ordered Subsets EM)**: Accelerated MLEM

Popular reconstruction tools:
- **STIR** (Software for Tomographic Image Reconstruction)
- **CASToR** (Customizable and Advanced Software for Tomographic Reconstruction)
- **NiftyRec** (GPU-accelerated reconstruction)

### Analyzing Results with ROOT

Use ROOT to inspect the raw event data:

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

// Detector head distribution
Singles->Draw("headID")

// Crystal positions
Singles->Draw("globalPosY:globalPosZ", "headID==0")

// Time distribution (for rotation studies)
Singles->Draw("time")
```

### Quality Control

To verify sinogram quality:

1. **Check counts**: Total counts should match expected activity × time × sensitivity
2. **Uniformity**: Uniform source should produce uniform projection
3. **Center of rotation**: Point source should trace sine wave in sinogram
4. **Resolution**: Point sources should appear as sharp peaks

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
