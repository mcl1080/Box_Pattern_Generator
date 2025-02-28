# Box Template Generator

A Python tool for creating SVG templates for custom-sized cardboard/paperboard boxes. This generator produces a cutting pattern that can be folded into a complete box. Cut the black lines, fold the green lines.

## Features

- Automatically determines width, length, and height based on dimension sizes
- Creates SVG templates with appropriately sized flaps and tabs
- Supports multiple units (mm, cm, inches) with automatic conversion
- Automatically adjusts for material thickness to ensure internal dimensions match requirements
- Generates optimized SVG files ready for laser cutters

## Installation

No installation is required beyond standard Python. The script uses only the built-in Python libraries.

```bash
# Clone or download this repository, then run:
python Box_Pattern.py
```

## Usage

Run the script and follow the prompts:

```
$ python Box_Pattern.py

Box SVG Generator
============================================================
Note: Enter the INTERNAL dimensions of your desired box
You can use 'mm', 'cm', or 'in' units (default is mm if no unit specified)
------------------------------------------------------------

Enter first dimension (e.g., 50mm, 5cm, 2in): 50mm
Enter second dimension: 75mm
Enter third dimension: 100mm

Box dimensions (internal):
  Width: 50.0mm
  Length: 75.0mm
  Height: 100.0mm

Enter material thickness (default: 3mm): 2mm
Material thickness: 2.0mm

Enter flap length (default: 15mm): 20mm
Flap length: 20.0mm

Enter filename (default: box.svg): my_custom_box.svg

SVG file 'my_custom_box.svg' has been created successfully.
Total dimensions: 264.0mm × 154.0mm
```

## Parameters

- **Dimensions**: Enter three dimensions in any order. The script will automatically determine which is width, length, and height.
- **Material Thickness**: The thickness of your material (cardboard, paperboard, etc.) in mm, cm, or inches.
- **Flap Length**: The length of the closure flap in mm, cm, or inches.
- **Filename**: The name of the SVG file to be created.

## Output

The script generates an SVG file with:

- A complete cutting template for a box with tabs and flaps
- Length sides have extended tabs for closure clearance
- A tapered flap to glue the box closed
- Green highlights on lines that overlap (folding guide)
- Dimensions adjusted to ensure the internal box size matches your requirements


## Tips

- Use the SVG with a laser cutter or print it on paper and cut by hand
- Fold along the indicated lines to create your box
- Adjust the material thickness parameter to match your actual material