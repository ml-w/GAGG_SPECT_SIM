#!/usr/bin/env python3
"""
Simple visualization tool for reconstructed SPECT images

Usage:
    python visualize_reconstruction.py reconstructed_sirt.npy
    python visualize_reconstruction.py reconstruction/reconstructed_osem.npy
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys


def visualize_reconstruction(image_file):
    """
    Visualize reconstructed SPECT image

    Args:
        image_file: Path to .npy file containing reconstruction
    """
    # Load image
    image_path = Path(image_file)
    if not image_path.exists():
        print(f"Error: File not found: {image_file}")
        return

    image = np.load(image_path)

    print(f"Loaded: {image_file}")
    print(f"Shape: {image.shape}")
    print(f"Value range: [{np.min(image):.6f}, {np.max(image):.6f}]")
    print(f"Mean: {np.mean(image):.6f}, Std: {np.std(image):.6f}")

    # Create figure
    fig = plt.figure(figsize=(15, 5))

    # If 2D image
    if image.ndim == 2:
        # Show full image
        ax1 = plt.subplot(131)
        im1 = ax1.imshow(image, cmap='hot', aspect='auto')
        ax1.set_title('Reconstruction')
        ax1.axis('off')
        plt.colorbar(im1, ax=ax1)

        # Show with different colormap
        ax2 = plt.subplot(132)
        im2 = ax2.imshow(image, cmap='gray', aspect='auto')
        ax2.set_title('Gray scale')
        ax2.axis('off')
        plt.colorbar(im2, ax=ax2)

        # Show histogram
        ax3 = plt.subplot(133)
        ax3.hist(image.flatten(), bins=50, edgecolor='black', alpha=0.7)
        ax3.set_title('Intensity Histogram')
        ax3.set_xlabel('Intensity')
        ax3.set_ylabel('Frequency')
        ax3.grid(True, alpha=0.3)

    # If 3D volume
    elif image.ndim == 3:
        # Show central slices
        mid_z = image.shape[0] // 2
        mid_y = image.shape[1] // 2
        mid_x = image.shape[2] // 2

        ax1 = plt.subplot(131)
        im1 = ax1.imshow(image[mid_z, :, :], cmap='hot', aspect='auto')
        ax1.set_title(f'Axial Slice (z={mid_z})')
        ax1.axis('off')
        plt.colorbar(im1, ax=ax1)

        ax2 = plt.subplot(132)
        im2 = ax2.imshow(image[:, mid_y, :], cmap='hot', aspect='auto')
        ax2.set_title(f'Coronal Slice (y={mid_y})')
        ax2.axis('off')
        plt.colorbar(im2, ax=ax2)

        ax3 = plt.subplot(133)
        im3 = ax3.imshow(image[:, :, mid_x], cmap='hot', aspect='auto')
        ax3.set_title(f'Sagittal Slice (x={mid_x})')
        ax3.axis('off')
        plt.colorbar(im3, ax=ax3)

    plt.tight_layout()
    plt.savefig(image_path.parent / f"{image_path.stem}_visualization.png", dpi=150, bbox_inches='tight')
    print(f"\nSaved visualization: {image_path.parent / f'{image_path.stem}_visualization.png'}")

    plt.show()


def compare_reconstructions(files):
    """
    Compare multiple reconstructions side by side

    Args:
        files: List of reconstruction files to compare
    """
    images = []
    names = []

    for file in files:
        path = Path(file)
        if path.exists():
            images.append(np.load(path))
            names.append(path.stem.replace('reconstructed_', ''))
        else:
            print(f"Warning: Skipping {file} (not found)")

    if not images:
        print("No valid images to compare")
        return

    n = len(images)
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 5))

    if n == 1:
        axes = [axes]

    for i, (image, name) in enumerate(zip(images, names)):
        # For 2D images
        if image.ndim == 2:
            im = axes[i].imshow(image, cmap='hot', aspect='auto')
        # For 3D, show central slice
        else:
            mid_z = image.shape[0] // 2
            im = axes[i].imshow(image[mid_z, :, :], cmap='hot', aspect='auto')

        axes[i].set_title(name.upper())
        axes[i].axis('off')
        plt.colorbar(im, ax=axes[i])

    plt.tight_layout()
    plt.savefig(Path(files[0]).parent / "reconstruction_comparison.png", dpi=150, bbox_inches='tight')
    print(f"\nSaved comparison: {Path(files[0]).parent / 'reconstruction_comparison.png'}")

    plt.show()


def main():
    """Main execution"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Visualize single reconstruction:")
        print("    python visualize_reconstruction.py reconstructed_sirt.npy")
        print("\n  Compare multiple reconstructions:")
        print("    python visualize_reconstruction.py reconstructed_fbp.npy reconstructed_sirt.npy reconstructed_mlem.npy")
        return 1

    files = sys.argv[1:]

    if len(files) == 1:
        # Single visualization
        visualize_reconstruction(files[0])
    else:
        # Compare multiple
        compare_reconstructions(files)

    return 0


if __name__ == "__main__":
    exit(main())
