#!/usr/bin/env python3
"""
Simple test script for GAGG SPECT configuration system
No external dependencies required (except for simulation run)
"""

from gagg_spect_config import (
    SPECTConfig,
    ScintillatorConfig,
    CollimatorConfig,
    FOVConfig,
    DetectorConfig,
)


def test_default_configs():
    """Test default configurations"""
    print("\n" + "="*70)
    print("Testing Default Configurations")
    print("="*70)

    # Test small animal
    config1 = SPECTConfig.default_small_animal()
    print("\n✅ Small animal config created")
    assert config1.validate()
    print("✅ Validation passed")

    # Test clinical
    config2 = SPECTConfig.default_clinical()
    print("✅ Clinical config created")
    assert config2.validate()
    print("✅ Validation passed")


def test_custom_scintillator():
    """Test custom scintillator dimensions"""
    print("\n" + "="*70)
    print("Testing Custom Scintillator Dimensions")
    print("="*70)

    # Test different crystal sizes
    sizes = [1.5, 2.0, 3.0, 4.0, 5.0]

    for size in sizes:
        config = SPECTConfig(
            name=f"test_{size}mm",
            detector=DetectorConfig(
                scintillator=ScintillatorConfig(
                    crystal_size_x=size,
                    crystal_size_y=size,
                    crystal_thickness=10.0,
                    array_size_x=100,
                    array_size_y=100,
                )
            )
        )

        assert config.validate()
        print(f"✅ {size}mm crystals: "
              f"{config.detector.scintillator.get_total_crystals():,} crystals, "
              f"detector size {config.detector.scintillator.detector_size_x:.1f} mm")


def test_custom_fov():
    """Test custom FOV configurations"""
    print("\n" + "="*70)
    print("Testing Custom FOV Configurations")
    print("="*70)

    fov_configs = [
        FOVConfig.small_fov(),
        FOVConfig.medium_fov(),
        FOVConfig.large_fov(),
        FOVConfig(radius=7.5, height=15, detector_radius=15, name="custom"),
    ]

    for fov in fov_configs:
        config = SPECTConfig(
            name=f"test_{fov.name}",
            fov=fov,
        )
        assert config.validate()
        print(f"✅ {fov.name}: Ø{fov.diameter} cm × {fov.height} cm, "
              f"detector @ {fov.detector_radius} cm")


def test_json_serialization():
    """Test JSON save/load"""
    print("\n" + "="*70)
    print("Testing JSON Serialization")
    print("="*70)

    # Create config
    config1 = SPECTConfig.default_small_animal()
    config1.name = "test_json"

    # Save to JSON
    json_str = config1.to_json("test_config.json")
    print("✅ Saved to test_config.json")

    # Load from JSON
    config2 = SPECTConfig.from_json("test_config.json")
    print("✅ Loaded from test_config.json")

    # Verify
    assert config2.name == "test_json"
    assert config2.detector.scintillator.crystal_size_x == 3.0
    print("✅ Data integrity verified")


def test_collimator_types():
    """Test different collimator configurations"""
    print("\n" + "="*70)
    print("Testing Collimator Configurations")
    print("="*70)

    # Pinhole
    config1 = SPECTConfig(
        name="pinhole_test",
        detector=DetectorConfig(
            collimator=CollimatorConfig(
                type="pinhole",
                pinhole_diameter=1.5,
            )
        )
    )
    assert config1.validate()
    print("✅ Pinhole collimator: 1.5 mm aperture")

    # Parallel hole
    config2 = SPECTConfig(
        name="parallel_test",
        detector=DetectorConfig(
            collimator=CollimatorConfig(
                type="parallel",
                parallel_hole_diameter=1.5,
                parallel_septa_thickness=0.2,
                parallel_hole_length=35.0,
            )
        )
    )
    assert config2.validate()
    print("✅ Parallel-hole collimator: 1.5 mm holes, 35 mm length")


def test_head_configurations():
    """Test different numbers of detector heads"""
    print("\n" + "="*70)
    print("Testing Detector Head Configurations")
    print("="*70)

    for n_heads in [1, 2, 3, 4]:
        config = SPECTConfig(
            name=f"test_{n_heads}heads",
            detector=DetectorConfig(number_of_heads=n_heads)
        )
        assert config.validate()
        angles = config.detector.get_head_angles()
        print(f"✅ {n_heads} head(s): angles = {angles}")


def test_validation():
    """Test configuration validation"""
    print("\n" + "="*70)
    print("Testing Configuration Validation")
    print("="*70)

    # Valid config
    config = SPECTConfig.default_small_animal()
    assert config.validate()
    print("✅ Valid configuration passed")

    # Invalid: detector radius < FOV radius
    config_invalid = SPECTConfig(
        fov=FOVConfig(
            radius=10.0,
            detector_radius=5.0,  # Too close!
            height=10.0,
        )
    )
    assert not config_invalid.validate()
    print("✅ Invalid configuration correctly rejected")


def generate_example_configs():
    """Generate example configuration files"""
    print("\n" + "="*70)
    print("Generating Example Configuration Files")
    print("="*70)

    examples = [
        ("small_animal", SPECTConfig.default_small_animal()),
        ("clinical", SPECTConfig.default_clinical()),
    ]

    # High resolution
    high_res = SPECTConfig(
        name="GAGG_SPECT_HighRes",
        detector=DetectorConfig(
            scintillator=ScintillatorConfig(
                crystal_size_x=2.0,
                crystal_size_y=2.0,
                crystal_thickness=12.0,
                array_size_x=200,
                array_size_y=200,
            )
        ),
        fov=FOVConfig.small_fov(),
    )
    examples.append(("high_resolution", high_res))

    # Custom FOV
    custom_fov = SPECTConfig.default_small_animal()
    custom_fov.name = "GAGG_SPECT_CustomFOV"
    custom_fov.fov = FOVConfig(
        radius=7.5, height=15, detector_radius=15, name="custom_15cm"
    )
    examples.append(("custom_fov", custom_fov))

    for name, config in examples:
        filename = f"example_{name}.json"
        config.to_json(filename)
        print(f"✅ Generated: {filename}")

    print(f"\n✅ Generated {len(examples)} example configurations")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("GAGG SPECT Configuration System Test Suite")
    print("="*70)

    try:
        test_default_configs()
        test_custom_scintillator()
        test_custom_fov()
        test_json_serialization()
        test_collimator_types()
        test_head_configurations()
        test_validation()
        generate_example_configs()

        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED!")
        print("="*70)
        print("\nConfiguration system is working correctly.")
        print("Example configurations have been generated.\n")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
