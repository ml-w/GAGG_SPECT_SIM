#!/bin/bash
# Setup and test script for OpenGATE SPECT examples

set -e  # Exit on error

echo "=========================================="
echo "OpenGATE SPECT Examples - Setup & Test"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"
echo ""

# Check if we're in a virtual environment (recommended)
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo "⚠️  WARNING: Not in a virtual environment"
    echo "   It's recommended to use a virtual environment:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting. Please activate a virtual environment and try again."
        exit 1
    fi
fi

# Install requirements
echo "=========================================="
echo "Installing requirements..."
echo "=========================================="
echo ""

if [[ -f "requirements_opengate.txt" ]]; then
    pip install -r requirements_opengate.txt
    echo ""
    echo "✓ Requirements installed"
else
    echo "❌ requirements_opengate.txt not found"
    echo "   Installing core dependencies manually..."
    pip install opengate numpy scipy itk SimpleITK matplotlib
fi

echo ""
echo "=========================================="
echo "Verifying OpenGATE installation..."
echo "=========================================="
echo ""

# Test OpenGATE import
python3 << EOF
try:
    import opengate as gate
    print(f"✓ OpenGATE version: {gate.__version__}")

    # Check for SPECT contrib
    from opengate.contrib.spect import spect_config
    print("✓ SPECT contrib module found")

    from opengate.contrib.spect import ge_discovery_nm670
    print("✓ GE Discovery NM670 module found")

    from opengate.contrib.spect import siemens_intevo
    print("✓ Siemens Intevo module found")

    print("\n✓ All required modules are available")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nPlease ensure OpenGATE is properly installed:")
    print("  pip install opengate")
    exit(1)
EOF

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ OpenGATE verification failed"
    echo "   Please install OpenGATE manually:"
    echo "   pip install opengate"
    exit 1
fi

echo ""
echo "=========================================="
echo "Running syntax check on examples..."
echo "=========================================="
echo ""

# Check syntax of example files
for example in example_opengate_spect.py example_spect_config.py; do
    if [[ -f "$example" ]]; then
        echo "Checking $example..."
        python3 -m py_compile "$example"
        if [ $? -eq 0 ]; then
            echo "✓ $example syntax OK"
        else
            echo "❌ $example has syntax errors"
            exit 1
        fi
    else
        echo "⚠️  $example not found"
    fi
done

echo ""
echo "=========================================="
echo "Running quick test (dry run)..."
echo "=========================================="
echo ""

# Test that we can at least import and initialize configs
python3 << 'EOF'
import sys
import opengate as gate

print("Testing Example 1: Direct API...")
try:
    # Import the module (but don't run the full simulation)
    sys.path.insert(0, '.')

    # Just test imports and config creation
    from example_opengate_spect import SPECTSimulationConfig
    config = SPECTSimulationConfig()
    config.acquisition_time = 1  # Short test
    config.source_activity = 1e3  # Low activity for test

    print(f"✓ Configuration created successfully")
    print(f"  Detector: {config.detector_model}")
    print(f"  FOV: {config.fov_size} cm")
    print(f"  Pixel size: {config.pixel_size} cm")

except Exception as e:
    print(f"❌ Error in example_opengate_spect.py: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nTesting Example 2: SPECTConfig API...")
try:
    from opengate.contrib.spect import spect_config

    # Create a minimal config
    config = spect_config.SPECTConfig()
    config.detector = spect_config.DetectorConfig()
    config.detector.model = "Intevo"
    config.detector.collimator = "lehr"

    config.acquisition = spect_config.AcquisitionConfig()
    config.acquisition.radius = 30
    config.acquisition.duration = 1

    print(f"✓ SPECTConfig created successfully")
    print(f"  Detector: {config.detector.model}")
    print(f"  Collimator: {config.detector.collimator}")
    print(f"  Radius: {config.acquisition.radius} cm")

except Exception as e:
    print(f"❌ Error with SPECTConfig: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✓ All dry run tests passed!")
EOF

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Test failed"
    exit 1
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "✓ OpenGATE is installed and working"
echo "✓ SPECT contrib modules are available"
echo "✓ Example scripts are ready to run"
echo ""
echo "Next steps:"
echo ""
echo "1. Run Example 1 (Direct API):"
echo "   python3 example_opengate_spect.py"
echo ""
echo "2. Run Example 2 (SPECTConfig):"
echo "   python3 example_spect_config.py"
echo ""
echo "3. Customize the configuration in either script"
echo "   Edit SPECTSimulationConfig class or SPECTConfig objects"
echo ""
echo "4. Read the documentation:"
echo "   cat README_OPENGATE_EXAMPLES.md"
echo ""
echo "=========================================="
echo ""

# Optional: Ask if user wants to run a quick test simulation
read -p "Run a quick 5-second test simulation? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Running quick test simulation..."
    echo "This will take about 1-2 minutes..."
    echo ""

    # Create a minimal test script
    python3 << 'EOF'
import opengate as gate
from opengate.contrib.spect.siemens_intevo import add_spect_head
from pathlib import Path

print("Creating minimal test simulation...")

# Create simulation
sim = gate.Simulation()
sim.g4_verbose = False
sim.visu = False
sim.random_seed = 42
sim.number_of_threads = 2

# Small world
sim.world.size = [50 * gate.cm, 50 * gate.cm, 50 * gate.cm]
sim.world.material = "G4_AIR"

# Add physics
sim.physics_manager.physics_list_name = "G4EmStandardPhysics_option4"

# Add one detector head
head, colli, crystal = add_spect_head(sim, "test_head", "lehr")
head.translation = [30 * gate.cm, 0, 0]

# Add simple source
source = sim.add_source("GenericSource", "test_source")
source.particle = "gamma"
source.energy.type = "mono"
source.energy.mono = 140.5 * gate.keV
source.position.type = "point"
source.direction.type = "iso"
source.activity = 1e4 * gate.Bq

# Short acquisition
sim.run_timing_intervals = [[0, 2 * gate.s]]

# Output
output_dir = Path("./test_output")
output_dir.mkdir(exist_ok=True)

# Minimal digitizer
hc = sim.add_actor("DigitizerHitsCollectionActor", "Hits")
hc.attached_to = crystal.name
hc.output_filename = output_dir / "test_hits.root"

print("Running simulation (2 seconds)...")
sim.run()

print("\n✓ Test simulation completed successfully!")
print(f"  Output: {output_dir}")

# Cleanup
import shutil
shutil.rmtree(output_dir, ignore_errors=True)
print("  (Test output cleaned up)")
EOF

    if [ $? -eq 0 ]; then
        echo ""
        echo "✓ Test simulation successful!"
        echo "  Your setup is fully functional."
    else
        echo ""
        echo "❌ Test simulation failed"
        echo "   This might be due to missing Geant4 libraries."
        echo "   The examples might still work with a full simulation."
    fi
fi

echo ""
echo "Setup script completed."
echo ""
