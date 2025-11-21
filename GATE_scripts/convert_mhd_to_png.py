#!/usr/bin/env python3
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import itk

def convert_mhd_to_png(mhd_filename, output_filename=None):
    if not os.path.exists(mhd_filename):
        print(f"Error: File {mhd_filename} not found.")
        return

    if output_filename is None:
        output_filename = os.path.splitext(mhd_filename)[0] + ".png"

    try:
        # Read the image using ITK
        image = itk.imread(mhd_filename)
        # Get the array from the image
        array = itk.GetArrayFromImage(image)
        
        # The array might be 3D (1, Y, X) or 2D (Y, X). Squeeze it.
        array = np.squeeze(array)
        
        # Check dimensions
        if array.ndim != 2:
            print(f"Error: Expected 2D image, got {array.ndim}D.")
            return

        # Get image spacing and size to set aspect ratio correctly
        spacing = image.GetSpacing() # (sx, sy, sz)
        size = image.GetLargestPossibleRegion().GetSize() # (nx, ny, nz)
        
        # Physical dimensions
        phys_width = size[0] * spacing[0]
        phys_height = size[1] * spacing[1]
        
        print(f"Image Size: {size[0]} x {size[1]}")
        print(f"Spacing: {spacing[0]} x {spacing[1]}")
        print(f"Physical Dimensions: {phys_width:.2f} x {phys_height:.2f} mm")

        # Plotting
        plt.figure(figsize=(8, 8 * (phys_height / phys_width)))
        plt.imshow(array, cmap='gray', origin='lower', extent=[0, phys_width, 0, phys_height])
        plt.colorbar(label='Counts')
        plt.title(f"Projection: {os.path.basename(mhd_filename)}")
        plt.xlabel("X (mm)")
        plt.ylabel("Y (mm)")
        
        plt.tight_layout()
        plt.savefig(output_filename, dpi=300)
        print(f"Saved PNG to {output_filename}")
        plt.close()

    except Exception as e:
        print(f"Error converting {mhd_filename}: {e}")
        # Fallback: Try reading raw file directly if ITK fails
        try:
            print("Attempting fallback raw read...")
            raw_filename = os.path.splitext(mhd_filename)[0] + ".raw"
            if not os.path.exists(raw_filename):
                print(f"Raw file {raw_filename} not found.")
                return
            
            # Assume float32 (standard for GATE output usually)
            # We need to know the dimensions. Let's parse the MHD header simply.
            dim_x, dim_y = 128, 128 # Default from geometry_3.py
            dtype = np.float32
            
            with open(mhd_filename, 'r') as f:
                for line in f:
                    if line.startswith('DimSize'):
                        parts = line.split('=')[1].strip().split()
                        dim_x = int(parts[0])
                        dim_y = int(parts[1])
                    if line.startswith('ElementType'):
                        if 'MET_FLOAT' in line: dtype = np.float32
                        elif 'MET_DOUBLE' in line: dtype = np.float64
                        elif 'MET_SHORT' in line: dtype = np.int16
            
            data = np.fromfile(raw_filename, dtype=dtype)
            if data.size != dim_x * dim_y:
                print(f"Warning: Data size {data.size} does not match dimensions {dim_x}x{dim_y}. Reshaping might fail.")
            
            array = data.reshape((dim_y, dim_x))
            
            plt.figure()
            plt.imshow(array, cmap='gray', origin='lower')
            plt.colorbar()
            plt.title(f"Projection (Raw): {os.path.basename(mhd_filename)}")
            plt.savefig(output_filename)
            print(f"Saved PNG (fallback) to {output_filename}")
            plt.close()
            
        except Exception as e2:
            print(f"Fallback failed: {e2}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_mhd_to_png.py <file1.mhd> [file2.mhd ...]")
        # Auto-find mhd files in current directory if no args
        files = [f for f in os.listdir('.') if f.endswith('.mhd')]
        if files:
            print(f"Found {len(files)} .mhd files in current directory. Converting...")
            for f in files:
                convert_mhd_to_png(f)
    else:
        for f in sys.argv[1:]:
            convert_mhd_to_png(f)