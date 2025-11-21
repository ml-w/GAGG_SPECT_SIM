# Quick Start Guide - OpenGATE SPECT Examples

## Installation (5 minutes)

### 1. Install OpenGATE

```bash
pip install opengate
```

Or for the latest development version:

```bash
pip install git+https://github.com/OpenGATE/opengate.git
```

**Note:** The first time you import OpenGATE, it will automatically download Geant4 data files (~1-2 GB). This is a one-time download and may take 5-10 minutes.

### 2. Verify Installation

```bash
python3 -c "import opengate as gate; print('OpenGATE version:', gate.__version__)"
```

If you see the version number, you're ready to go!

## Running Your First Example (2 minutes)

### Option 1: Direct API Example

This example shows detailed control over detector configuration:

```bash
cd /home/user/GAGG_SPECT_SIM
python3 example_opengate_spect.py
```

**What it does:**
- Creates a SPECT simulation with GE NM670 or Siemens Intevo detector
- Configures 2 detector heads at 180° spacing
- Sets up a simple Tc-99m point source
- Runs a 20-second acquisition
- Generates projection images

**Output:** `./output_opengate_spect/`

### Option 2: SPECTConfig API Example

This example uses the high-level configuration class:

```bash
cd /home/user/GAGG_SPECT_SIM
python3 example_spect_config.py
```

**What it does:**
- Demonstrates the comprehensive SPECTConfig API
- Configures detector, phantom, source, and acquisition
- Shows how to save/load configurations
- More suitable for complex simulations

**Output:** `./output_spect_config/`

## Customizing the Simulation (5 minutes)

### Change Detector Model

Edit either example script and modify:

```python
# For example_opengate_spect.py
config.detector_model = "SIEMENS_INTEVO"  # or "GE_NM670"

# For example_spect_config.py
config.detector.model = "Intevo"  # or "NM670"
```

### Adjust Field of View

```python
# For example_opengate_spect.py
config.fov_size = [50, 50, 50]  # cm [x, y, z]

# For example_spect_config.py
config.phantom.size = [125, 125, 125]  # voxels
config.phantom.voxel_size = [0.4, 0.4, 0.4]  # cm
# FOV = 125 × 0.4 = 50 cm
```

### Change Crystal Type (GE NM670 only)

```python
# For example_opengate_spect.py
config.crystal_size = "5/8"  # 15.875mm (thicker crystal)

# For example_spect_config.py
config.detector.crystal_size = "5/8"
```

### Adjust Readout Resolution

```python
# For example_opengate_spect.py
config.pixel_size = [0.2, 0.2]  # cm (2mm pixels - higher resolution)

# For example_spect_config.py
config.detector.spatial_blur_fwhm = 0.2  # cm
```

### Multiple Detector Heads

```python
# For example_opengate_spect.py
config.num_heads = 3
config.head_angles = [0, 120, 240]  # 120° spacing

# For example_spect_config.py
config.detector.number_of_heads = 3
```

## Common Configurations

### High Resolution SPECT (Small Animal)

```python
config.detector_model = "GE_NM670"
config.crystal_size = "3/8"
config.collimator_type = "lehr"
config.pixel_size = [0.2, 0.2]  # 2mm pixels
config.detector_radius = 15  # cm - close to subject
config.fov_size = [20, 20, 20]  # cm
```

### Clinical SPECT (Human Imaging)

```python
config.detector_model = "SIEMENS_INTEVO"
config.collimator_type = "lehr"
config.pixel_size = [0.45, 0.45]  # 4.5mm pixels
config.detector_radius = 36  # cm
config.fov_size = [40, 40, 40]  # cm
config.num_heads = 2
```

### Fast Acquisition (Quick Testing)

```python
config.acquisition_time = 5  # seconds (vs. 20s default)
config.source_activity = 1e4  # Bq (vs. 1e6 default)
config.num_projections = 30  # (vs. 60 default)
config.number_of_threads = 8  # Use more CPU cores
```

## Troubleshooting

### "No module named 'opengate'"

```bash
pip install opengate
```

### Simulation takes too long

Reduce the simulation parameters:
```python
config.acquisition_time = 10  # Reduce from 20s
config.source_activity = 1e5  # Reduce from 1e6 Bq
config.number_of_threads = 8  # Increase if you have more cores
```

### Out of memory

```python
config.fov_size = [30, 30, 30]  # Reduce from 40x40x40
config.num_projections = 30  # Reduce from 60
```

### Geant4 data download fails

The script will retry automatically. If it continues to fail:
1. Check your internet connection
2. Try again later (CERN servers may be temporarily unavailable)
3. Or download manually from: https://geant4.web.cern.ch/support/download

## Next Steps

1. **Read the full documentation:**
   ```bash
   cat README_OPENGATE_EXAMPLES.md
   ```

2. **Explore the code:**
   - `example_opengate_spect.py` - Direct API with detailed comments
   - `example_spect_config.py` - High-level API with multiple examples

3. **View your results:**
   - ROOT files: Use ROOT or uproot to analyze
   - MHD/RAW files: Use ITK, SimpleITK, or ImageJ to visualize
   - Python visualization:
     ```python
     import SimpleITK as sitk
     import matplotlib.pyplot as plt

     img = sitk.ReadImage("output_opengate_spect/projection_head_0.mhd")
     array = sitk.GetArrayFromImage(img)
     plt.imshow(array[0], cmap='hot')
     plt.colorbar()
     plt.show()
     ```

4. **Customize for your research:**
   - Modify source distribution
   - Add custom phantoms
   - Implement gantry rotation
   - Export data in your preferred format

## Resources

- **OpenGATE Documentation:** http://opengate.readthedocs.io/
- **OpenGATE GitHub:** https://github.com/OpenGATE/opengate
- **SPECT Contrib Code:** https://github.com/OpenGATE/opengate/tree/master/opengate/contrib/spect
- **This Project:** README_OPENGATE_EXAMPLES.md

## Support

For issues with:
- **OpenGATE:** https://github.com/OpenGATE/opengate/issues
- **These examples:** Open an issue in the GAGG_SPECT_SIM repository

## Tips

1. **Start small:** Use short acquisition times and low activity for initial testing
2. **Use threads:** Set `number_of_threads` to match your CPU cores
3. **Save configs:** Use JSON serialization to save and share configurations
4. **Batch simulations:** Write a loop to run multiple configurations
5. **Validate:** Compare results with physical measurements or published data

Happy simulating! 🎯
