# CLAUDE.md - GAGG SPECT Simulation Project

## Project Overview

This is a GATE (Geant4 Application for Tomographic Emission) simulation for a SPECT imaging system using GAGG (Gd₃Al₂Ga₃O₁₂:Ce) scintillator crystals with pinhole collimation, designed for Tc-99m (140.5 keV) imaging.

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
├── README.md                 # Project documentation
├── CLAUDE.md                 # This file - task specifications
└── GATE_scripts/
    ├── main.mac              # Master simulation script
    ├── geometry.mac          # Detector geometry (3 heads, pinhole)
    ├── physics.mac           # Physics processes
    ├── digitizer.mac         # Detector response chain
    ├── source.mac            # Tc-99m point sources
    ├── output.mac            # ROOT and projection output
    ├── verbose.mac           # Logging settings
    └── visu.mac              # Visualization
```

## Key Simulation Parameters

- **Scintillator**: GAGG crystals (3mm × 3mm × 10mm)
- **Crystal array**: 160 × 160 per head
- **Detector heads**: 3 at 120° spacing
- **Collimator**: Tungsten pinhole (1.5mm aperture)
- **Source**: Tc-99m (140.5 keV)
- **Energy resolution**: 7% @ 140.5 keV
- **Energy window**: 126.5–154.5 keV (±10%)
