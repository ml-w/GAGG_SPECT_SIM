#!/usr/bin/env python3
"""
GAGG SPECT Configuration System
================================
Configurable SPECT setup inspired by OpenGATE contrib/spect/spect_config.py
Allows control of scintillator dimensions, FOV, and system parameters.

Author: Claude
Date: 2025-11-21
"""

import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Tuple, Dict

# OpenGATE import is optional for configuration only
# It's only required when actually running simulations
try:
    import opengate as gate
    OPENGATE_AVAILABLE = True
except ImportError:
    OPENGATE_AVAILABLE = False
    gate = None


# ==============================================================================
# Base Configuration Class
# ==============================================================================

class ConfigBase:
    """Base class providing JSON serialization/deserialization"""

    def to_dict(self) -> dict:
        """Convert configuration to dictionary"""
        return asdict(self)

    def to_json(self, filepath: Optional[str] = None) -> str:
        """
        Convert configuration to JSON string or save to file

        Parameters:
        -----------
        filepath : str, optional
            If provided, save JSON to this file

        Returns:
        --------
        str : JSON string representation
        """
        json_str = json.dumps(self.to_dict(), indent=2)
        if filepath:
            Path(filepath).write_text(json_str)
        return json_str

    @classmethod
    def from_json(cls, json_str_or_path: str):
        """
        Create configuration from JSON string or file

        Parameters:
        -----------
        json_str_or_path : str
            JSON string or path to JSON file

        Returns:
        --------
        ConfigBase : Configuration instance
        """
        if Path(json_str_or_path).exists():
            json_str = Path(json_str_or_path).read_text()
        else:
            json_str = json_str_or_path

        data = json.loads(json_str)

        # For nested dataclasses, we need to convert dicts back to objects
        # This is handled in the SPECTConfig.from_json override
        return cls(**data)

    @classmethod
    def from_dict(cls, data: dict):
        """
        Create configuration from dictionary

        Parameters:
        -----------
        data : dict
            Dictionary with configuration data

        Returns:
        --------
        ConfigBase : Configuration instance
        """
        return cls(**data)


# ==============================================================================
# Scintillator Configuration
# ==============================================================================

@dataclass
class ScintillatorConfig(ConfigBase):
    """
    Configuration for GAGG scintillator crystals

    Attributes:
    -----------
    crystal_size_x : float
        Crystal width in X direction (mm)
    crystal_size_y : float
        Crystal width in Y direction (mm)
    crystal_thickness : float
        Crystal thickness/depth in Z direction (mm)
    crystal_spacing : float
        Gap between crystals (mm)
    array_size_x : int
        Number of crystals in X direction
    array_size_y : int
        Number of crystals in Y direction
    material : str
        Scintillator material name (must be in material database)
    """

    # Crystal dimensions (mm)
    crystal_size_x: float = 3.0
    crystal_size_y: float = 3.0
    crystal_thickness: float = 10.0

    # Crystal spacing (mm)
    crystal_spacing: float = 0.1

    # Array configuration
    array_size_x: int = 160
    array_size_y: int = 160

    # Material
    material: str = "GAGG"

    @property
    def pixel_pitch_x(self) -> float:
        """Total pitch including crystal and gap in X (mm)"""
        return self.crystal_size_x + self.crystal_spacing

    @property
    def pixel_pitch_y(self) -> float:
        """Total pitch including crystal and gap in Y (mm)"""
        return self.crystal_size_y + self.crystal_spacing

    @property
    def detector_size_x(self) -> float:
        """Total detector size in X (mm)"""
        return self.array_size_x * self.pixel_pitch_x

    @property
    def detector_size_y(self) -> float:
        """Total detector size in Y (mm)"""
        return self.array_size_y * self.pixel_pitch_y

    def get_total_crystals(self) -> int:
        """Get total number of crystals in array"""
        return self.array_size_x * self.array_size_y


# ==============================================================================
# Collimator Configuration
# ==============================================================================

@dataclass
class CollimatorConfig(ConfigBase):
    """
    Configuration for pinhole or parallel-hole collimator

    Attributes:
    -----------
    type : str
        Collimator type: "pinhole" or "parallel"
    material : str
        Collimator material (Lead, Tungsten, etc.)
    thickness : float
        Collimator thickness (mm)
    pinhole_diameter : float
        Pinhole aperture diameter (mm), used if type="pinhole"
    pinhole_cone_angle : float
        Cone opening angle for pinhole (degrees)
    parallel_hole_diameter : float
        Hole diameter for parallel collimator (mm)
    parallel_septa_thickness : float
        Septa thickness for parallel collimator (mm)
    parallel_hole_length : float
        Hole length/height for parallel collimator (mm)
    """

    type: str = "pinhole"  # "pinhole" or "parallel"
    material: str = "Tungsten"
    thickness: float = 5.0  # mm

    # Pinhole parameters
    pinhole_diameter: float = 1.5  # mm (entrance aperture)
    pinhole_cone_angle: float = 30.0  # degrees

    # Parallel hole parameters
    parallel_hole_diameter: float = 1.5  # mm
    parallel_septa_thickness: float = 0.2  # mm
    parallel_hole_length: float = 25.0  # mm


# ==============================================================================
# Field of View Configuration
# ==============================================================================

@dataclass
class FOVConfig(ConfigBase):
    """
    Configuration for Field of View

    Attributes:
    -----------
    radius : float
        FOV radius (cm)
    height : float
        FOV height (cm)
    detector_radius : float
        Distance from FOV center to detector face (cm)
    name : str
        Descriptive name for this FOV configuration
    """

    radius: float = 5.0  # cm
    height: float = 10.0  # cm
    detector_radius: float = 10.0  # cm
    name: str = "small_fov"

    @property
    def diameter(self) -> float:
        """FOV diameter (cm)"""
        return 2.0 * self.radius

    @classmethod
    def small_fov(cls):
        """Preset: Small FOV (10 cm diameter) for small animal imaging"""
        return cls(
            radius=5.0,
            height=10.0,
            detector_radius=10.0,
            name="small_fov_10cm"
        )

    @classmethod
    def large_fov(cls):
        """Preset: Large FOV (80 cm diameter) for clinical imaging"""
        return cls(
            radius=40.0,
            height=50.0,
            detector_radius=60.0,
            name="large_fov_80cm"
        )

    @classmethod
    def medium_fov(cls):
        """Preset: Medium FOV (30 cm diameter) for primate imaging"""
        return cls(
            radius=15.0,
            height=25.0,
            detector_radius=25.0,
            name="medium_fov_30cm"
        )


# ==============================================================================
# Detector Head Configuration
# ==============================================================================

@dataclass
class DetectorConfig(ConfigBase):
    """
    Configuration for SPECT detector head

    Attributes:
    -----------
    number_of_heads : int
        Number of detector heads (1-4)
    scintillator : ScintillatorConfig
        Scintillator crystal configuration
    collimator : CollimatorConfig
        Collimator configuration
    shielding_material : str
        Shielding material (Lead, etc.)
    shielding_thickness : float
        Shielding thickness (mm)
    backside_thickness : float
        Electronics/PMT backing thickness (mm)
    backside_material : str
        Backing material
    """

    number_of_heads: int = 3
    scintillator: ScintillatorConfig = field(default_factory=ScintillatorConfig)
    collimator: CollimatorConfig = field(default_factory=CollimatorConfig)

    # Shielding
    shielding_material: str = "Lead"
    shielding_thickness: float = 5.0  # mm

    # Backside (PMT/electronics)
    backside_thickness: float = 50.0  # mm
    backside_material: str = "Glass"

    def get_head_angles(self) -> List[float]:
        """Get starting angles for each detector head (degrees)"""
        if self.number_of_heads == 1:
            return [0.0]
        elif self.number_of_heads == 2:
            return [0.0, 180.0]
        elif self.number_of_heads == 3:
            return [0.0, 120.0, 240.0]
        elif self.number_of_heads == 4:
            return [0.0, 90.0, 180.0, 270.0]
        else:
            raise ValueError(f"Invalid number_of_heads: {self.number_of_heads}. Must be 1-4.")


# ==============================================================================
# Acquisition Configuration
# ==============================================================================

@dataclass
class AcquisitionConfig(ConfigBase):
    """
    Configuration for SPECT acquisition

    Attributes:
    -----------
    duration : float
        Total acquisition duration (seconds)
    rotation_enabled : bool
        Enable detector rotation for tomographic acquisition
    rotation_speed : float
        Rotation speed (degrees/second), 0 for static
    number_of_projections : int
        Number of projections for tomographic acquisition
    time_per_projection : float
        Time per projection (seconds)
    """

    duration: float = 60.0  # seconds
    rotation_enabled: bool = True
    rotation_speed: float = 6.0  # deg/s (360 degrees in 60 seconds)
    number_of_projections: int = 60

    @property
    def time_per_projection(self) -> float:
        """Time per projection (seconds)"""
        if self.number_of_projections > 0:
            return self.duration / self.number_of_projections
        return self.duration

    @property
    def angle_per_projection(self) -> float:
        """Angular step per projection (degrees)"""
        return 360.0 / self.number_of_projections if self.number_of_projections > 0 else 0.0


# ==============================================================================
# Source Configuration
# ==============================================================================

@dataclass
class SourceConfig(ConfigBase):
    """
    Configuration for radioactive source

    Attributes:
    -----------
    isotope : str
        Isotope name (Tc99m, I123, etc.)
    energy : float
        Primary gamma energy (keV)
    activity : float
        Source activity (Bq)
    position : Tuple[float, float, float]
        Source position (x, y, z) in mm
    geometry_type : str
        Source geometry: "point", "sphere", "cylinder"
    geometry_radius : float
        Radius for sphere/cylinder sources (mm)
    geometry_height : float
        Height for cylinder sources (mm)
    """

    isotope: str = "Tc99m"
    energy: float = 140.5  # keV
    activity: float = 1e6  # Bq (1 MBq)

    # Position (mm)
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)

    # Geometry
    geometry_type: str = "point"  # "point", "sphere", "cylinder"
    geometry_radius: float = 1.0  # mm
    geometry_height: float = 10.0  # mm


# ==============================================================================
# Digitizer Configuration
# ==============================================================================

@dataclass
class DigitizerConfig(ConfigBase):
    """
    Configuration for detector digitizer chain

    Attributes:
    -----------
    energy_resolution : float
        Energy resolution (FWHM) at reference energy as fraction (e.g., 0.07 for 7%)
    energy_reference : float
        Reference energy for energy resolution (keV)
    energy_window_min : float
        Lower energy threshold (keV)
    energy_window_max : float
        Upper energy threshold (keV)
    projection_size : Tuple[int, int]
        Projection image size (pixels)
    projection_spacing : Tuple[float, float]
        Projection pixel spacing (mm)
    """

    energy_resolution: float = 0.07  # 7% FWHM at 140.5 keV
    energy_reference: float = 140.5  # keV

    # Energy window (±10% around photopeak)
    energy_window_min: float = 126.5  # keV
    energy_window_max: float = 154.5  # keV

    # Projection parameters (usually match detector array)
    projection_size: Tuple[int, int] = (160, 160)
    projection_spacing: Tuple[float, float] = (3.1, 3.1)  # mm


# ==============================================================================
# Main SPECT Configuration
# ==============================================================================

@dataclass
class SPECTConfig(ConfigBase):
    """
    Main configuration for GAGG SPECT system

    Attributes:
    -----------
    name : str
        Configuration name/identifier
    output_dir : str
        Output directory for simulation results
    detector : DetectorConfig
        Detector configuration
    fov : FOVConfig
        Field of view configuration
    acquisition : AcquisitionConfig
        Acquisition parameters
    source : SourceConfig
        Source configuration
    digitizer : DigitizerConfig
        Digitizer parameters
    physics_list : str
        Geant4 physics list name
    """

    name: str = "GAGG_SPECT"
    output_dir: str = "output"

    detector: DetectorConfig = field(default_factory=DetectorConfig)
    fov: FOVConfig = field(default_factory=FOVConfig)
    acquisition: AcquisitionConfig = field(default_factory=AcquisitionConfig)
    source: SourceConfig = field(default_factory=SourceConfig)
    digitizer: DigitizerConfig = field(default_factory=DigitizerConfig)

    # Physics
    physics_list: str = "G4EmStandardPhysics_option4"

    # Materials database
    materials_database: Optional[str] = None

    @classmethod
    def default_small_animal(cls):
        """Preset: Small animal SPECT configuration"""
        config = cls(
            name="GAGG_SPECT_SmallAnimal",
            detector=DetectorConfig(
                number_of_heads=3,
                scintillator=ScintillatorConfig(
                    crystal_size_x=3.0,
                    crystal_size_y=3.0,
                    crystal_thickness=10.0,
                    array_size_x=160,
                    array_size_y=160,
                ),
                collimator=CollimatorConfig(
                    type="pinhole",
                    pinhole_diameter=1.5,
                )
            ),
            fov=FOVConfig.small_fov(),
            acquisition=AcquisitionConfig(
                duration=60.0,
                rotation_enabled=True,
                number_of_projections=60,
            )
        )
        return config

    @classmethod
    def default_clinical(cls):
        """Preset: Clinical SPECT configuration"""
        config = cls(
            name="GAGG_SPECT_Clinical",
            detector=DetectorConfig(
                number_of_heads=3,
                scintillator=ScintillatorConfig(
                    crystal_size_x=3.0,
                    crystal_size_y=3.0,
                    crystal_thickness=10.0,
                    array_size_x=200,
                    array_size_y=200,
                ),
                collimator=CollimatorConfig(
                    type="parallel",
                    parallel_hole_diameter=1.5,
                    parallel_septa_thickness=0.2,
                    parallel_hole_length=25.0,
                )
            ),
            fov=FOVConfig.large_fov(),
            acquisition=AcquisitionConfig(
                duration=300.0,
                rotation_enabled=True,
                number_of_projections=120,
            )
        )
        return config

    @classmethod
    def from_json(cls, json_str_or_path: str):
        """
        Create SPECTConfig from JSON, handling nested dataclasses

        Parameters:
        -----------
        json_str_or_path : str
            JSON string or path to JSON file

        Returns:
        --------
        SPECTConfig : Configuration instance
        """
        if Path(json_str_or_path).exists():
            json_str = Path(json_str_or_path).read_text()
        else:
            json_str = json_str_or_path

        data = json.loads(json_str)

        # Convert nested dicts to dataclass instances
        if "detector" in data and isinstance(data["detector"], dict):
            detector_data = data["detector"]
            if "scintillator" in detector_data and isinstance(detector_data["scintillator"], dict):
                detector_data["scintillator"] = ScintillatorConfig(**detector_data["scintillator"])
            if "collimator" in detector_data and isinstance(detector_data["collimator"], dict):
                detector_data["collimator"] = CollimatorConfig(**detector_data["collimator"])
            data["detector"] = DetectorConfig(**detector_data)

        if "fov" in data and isinstance(data["fov"], dict):
            data["fov"] = FOVConfig(**data["fov"])

        if "acquisition" in data and isinstance(data["acquisition"], dict):
            data["acquisition"] = AcquisitionConfig(**data["acquisition"])

        if "source" in data and isinstance(data["source"], dict):
            # Convert list to tuple for position
            if "position" in data["source"] and isinstance(data["source"]["position"], list):
                data["source"]["position"] = tuple(data["source"]["position"])
            data["source"] = SourceConfig(**data["source"])

        if "digitizer" in data and isinstance(data["digitizer"], dict):
            # Convert lists to tuples
            if "projection_size" in data["digitizer"] and isinstance(data["digitizer"]["projection_size"], list):
                data["digitizer"]["projection_size"] = tuple(data["digitizer"]["projection_size"])
            if "projection_spacing" in data["digitizer"] and isinstance(data["digitizer"]["projection_spacing"], list):
                data["digitizer"]["projection_spacing"] = tuple(data["digitizer"]["projection_spacing"])
            data["digitizer"] = DigitizerConfig(**data["digitizer"])

        return cls(**data)

    def validate(self) -> bool:
        """Validate configuration parameters"""
        errors = []

        # Check detector configuration
        if self.detector.number_of_heads < 1 or self.detector.number_of_heads > 4:
            errors.append("number_of_heads must be between 1 and 4")

        # Check scintillator dimensions
        if self.detector.scintillator.crystal_size_x <= 0:
            errors.append("crystal_size_x must be positive")
        if self.detector.scintillator.crystal_size_y <= 0:
            errors.append("crystal_size_y must be positive")
        if self.detector.scintillator.crystal_thickness <= 0:
            errors.append("crystal_thickness must be positive")

        # Check FOV
        if self.fov.radius <= 0:
            errors.append("FOV radius must be positive")
        if self.fov.detector_radius <= self.fov.radius:
            errors.append("detector_radius must be greater than FOV radius")

        # Check acquisition
        if self.acquisition.duration <= 0:
            errors.append("acquisition duration must be positive")

        if errors:
            print("Configuration validation errors:")
            for error in errors:
                print(f"  - {error}")
            return False

        return True

    def print_summary(self):
        """Print configuration summary"""
        print(f"\n{'='*70}")
        print(f"GAGG SPECT Configuration: {self.name}")
        print(f"{'='*70}")

        print(f"\n📊 Detector Configuration:")
        print(f"  Number of heads: {self.detector.number_of_heads}")
        print(f"  Head angles: {self.detector.get_head_angles()}")

        print(f"\n💎 Scintillator (GAGG):")
        print(f"  Crystal size: {self.detector.scintillator.crystal_size_x} × "
              f"{self.detector.scintillator.crystal_size_y} × "
              f"{self.detector.scintillator.crystal_thickness} mm³")
        print(f"  Array size: {self.detector.scintillator.array_size_x} × "
              f"{self.detector.scintillator.array_size_y} crystals")
        print(f"  Total crystals: {self.detector.scintillator.get_total_crystals():,}")
        print(f"  Detector size: {self.detector.scintillator.detector_size_x:.1f} × "
              f"{self.detector.scintillator.detector_size_y:.1f} mm²")
        print(f"  Pixel pitch: {self.detector.scintillator.pixel_pitch_x:.2f} mm")

        print(f"\n🔍 Collimator:")
        print(f"  Type: {self.detector.collimator.type}")
        print(f"  Material: {self.detector.collimator.material}")
        if self.detector.collimator.type == "pinhole":
            print(f"  Pinhole diameter: {self.detector.collimator.pinhole_diameter} mm")
        else:
            print(f"  Hole diameter: {self.detector.collimator.parallel_hole_diameter} mm")
            print(f"  Septa thickness: {self.detector.collimator.parallel_septa_thickness} mm")

        print(f"\n🎯 Field of View:")
        print(f"  Name: {self.fov.name}")
        print(f"  Diameter: {self.fov.diameter} cm")
        print(f"  Height: {self.fov.height} cm")
        print(f"  Detector radius: {self.fov.detector_radius} cm")

        print(f"\n⏱️  Acquisition:")
        print(f"  Duration: {self.acquisition.duration} s")
        print(f"  Rotation: {'Enabled' if self.acquisition.rotation_enabled else 'Disabled'}")
        if self.acquisition.rotation_enabled:
            print(f"  Number of projections: {self.acquisition.number_of_projections}")
            print(f"  Time per projection: {self.acquisition.time_per_projection:.2f} s")
            print(f"  Angular step: {self.acquisition.angle_per_projection:.2f}°")

        print(f"\n☢️  Source:")
        print(f"  Isotope: {self.source.isotope}")
        print(f"  Energy: {self.source.energy} keV")
        print(f"  Activity: {self.source.activity:.2e} Bq")
        print(f"  Geometry: {self.source.geometry_type}")

        print(f"\n⚡ Digitizer:")
        print(f"  Energy resolution: {self.digitizer.energy_resolution*100:.1f}% @ "
              f"{self.digitizer.energy_reference} keV")
        print(f"  Energy window: {self.digitizer.energy_window_min}-"
              f"{self.digitizer.energy_window_max} keV")
        print(f"  Projection size: {self.digitizer.projection_size[0]} × "
              f"{self.digitizer.projection_size[1]} pixels")

        print(f"\n{'='*70}\n")


# ==============================================================================
# Example Usage
# ==============================================================================

if __name__ == "__main__":
    # Example 1: Create default small animal config
    config1 = SPECTConfig.default_small_animal()
    config1.print_summary()

    # Save to JSON
    config1.to_json("config_small_animal.json")
    print("✅ Saved configuration to: config_small_animal.json")

    # Example 2: Create custom configuration
    config2 = SPECTConfig(
        name="CustomGAGG",
        detector=DetectorConfig(
            number_of_heads=2,
            scintillator=ScintillatorConfig(
                crystal_size_x=2.0,  # Smaller crystals
                crystal_size_y=2.0,
                crystal_thickness=15.0,  # Thicker crystals
                array_size_x=200,
                array_size_y=200,
            )
        ),
        fov=FOVConfig(radius=7.5, height=15.0, detector_radius=15.0, name="custom_15cm"),
    )

    print("\n" + "="*70)
    print("Custom Configuration Example:")
    print("="*70)
    config2.print_summary()

    # Validate
    if config2.validate():
        print("✅ Configuration is valid!")
    else:
        print("❌ Configuration has errors!")
