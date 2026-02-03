# Parametric 3D CAD Model of Steel Girder Bridge

## Overview

This project implements a parametric, modular 3D CAD model of a short-span steel girder bridge using the pythonOCC library. The model is fully adjustable through parameters and follows an object-oriented architecture for maintainability and extensibility.

## Features

- **Parametric Design**: All dimensions and counts are adjustable through variables
- **Modular Architecture**: Component-based design using factory pattern
- **3D Visualization**: Interactive 3D viewer with customizable colors
- **Export Capabilities**: STEP and BREP file export support
- **Skew Support**: Optional skew angle (0-15 degrees)

## Bridge Components

The bridge model consists of three main components:

1. **Main Longitudinal Steel Girders** (I-sections)
   - Adjustable number of girders (≥ 3)
   - Parametric I-section geometry (depth, flange width, thickness)
   
2. **Concrete Deck Slab** (Rectangular prism)
   - Sits on top of girders
   - Adjustable thickness and overhang
   
3. **Parapets** (Safety barriers)
   - Left and right parapets
   - Adjustable width and height

## Architecture

The code follows the architecture outlined in `ARCH.txt`:

```
BridgeComponent (Base Class)
├── Girder (I-section)
├── Deck (Rectangular prism)
└── Parapet (Rectangular prism)

BridgeModel (Assembly Class)
├── compute_layout()
├── create_components()
├── position_components()
├── assemble()
├── display()
└── export()
```

## Requirements

- Python 3.7+
- pythonocc-core (pythonOCC)

### Installation

```bash
# Install pythonocc-core using conda (recommended)
conda install -c conda-forge pythonocc-core

# OR using pip (may require additional dependencies)
pip install pythonocc-core
```

## Usage

### Basic Usage

Simply run the main script:

```bash
python bridge_model.py
```

This will:
1. Create the bridge model with default parameters
2. Display it in an interactive 3D viewer
3. Optionally export to STEP/BREP files (if enabled)

### Customizing Parameters

Edit the parameters at the top of `bridge_model.py`:

```python
# Geometry & Layout
SPAN_LENGTH_L = 12000          # Total span length (mm)
N_GIRDERS = 3                  # Number of girders
GIRDER_CENTROID_SPACING = 3000 # Spacing between girders (mm)
GIRDER_OFFSET_FROM_EDGE = 500  # Overhang (mm)
SKEW_ANGLE = 10                # Skew angle (degrees)

# Main Girder (I-section)
GIRDER_SECTION_D = 900         # Depth (mm)
GIRDER_SECTION_BF = 300        # Flange width (mm)
GIRDER_SECTION_TF = 16         # Flange thickness (mm)
GIRDER_SECTION_TW = 10         # Web thickness (mm)

# Deck Slab
DECK_THICKNESS = 200           # Deck thickness (mm)

# Parapet
PARAPET_WIDTH = 300            # Parapet width (mm)
PARAPET_HEIGHT = 1000          # Parapet height (mm)

# Visualization & Output
SAVE_STEP = True               # Export STEP file
STEP_FILENAME = "bridge_model.step"
SAVE_BREP = True               # Export BREP file
BREP_FILENAME = "bridge_model.brep"
```

## Default Parameters

The default configuration creates a bridge with these specifications:

- **Units**: Millimeters (mm)
- **Span Length**: 12,000 mm (12 m)
- **Number of Girders**: 3
- **Girder Spacing**: 3,000 mm center-to-center
- **Overall Deck Width**: 7,000 mm
- **Deck Thickness**: 200 mm
- **Skew Angle**: 10 degrees
- **Girder I-section**: 900mm depth, 300mm flange width

## File Structure

```
project/
├── bridge_model.py              # Main script (complete solution)
├── draw_i_section.py            # I-section factory function
├── draw_rectangular_prism.py    # Rectangular prism factory
├── portal_frame.py              # Reference example
├── ARCH.txt                     # Architecture specification
├── README.md                    # This file
└── requirements.txt             # Python dependencies
```

## Code Structure

### Component Classes

All components inherit from `BridgeComponent` base class:

- `BridgeComponent`: Base class with shape manipulation methods
  - `set_shape()`: Store geometry
  - `get_shape()`: Retrieve geometry
  - `translate()`: Move component in 3D
  - `rotate()`: Rotate component around axis

- `Girder`: I-section steel girder
- `Deck`: Concrete deck slab
- `Parapet`: Safety barrier

### Bridge Model Class

The `BridgeModel` class orchestrates the entire assembly:

1. **compute_layout()**: Calculate derived dimensions (deck width, girder positions)
2. **create_components()**: Instantiate all girders, deck, and parapets
3. **position_components()**: Place components in 3D space
4. **assemble()**: Combine into single compound shape
5. **display()**: Visualize using OCC viewer
6. **export()**: Save to STEP/BREP files

## Visualization

The 3D viewer provides:

- **Interactive rotation**: Click and drag to rotate
- **Zoom**: Mouse wheel or pinch gesture
- **Pan**: Right-click and drag
- **Color coding**:
  - Girders: Steel gray (0.7, 0.7, 0.75)
  - Deck: Concrete gray (0.8, 0.8, 0.8)
  - Parapets: Light beige (0.9, 0.9, 0.85)

## Export Formats

### STEP Format (.step)

Industry-standard CAD exchange format, compatible with:
- AutoCAD
- SolidWorks
- CATIA
- Other CAD software

### BREP Format (.brep)

OpenCASCADE native format, useful for:
- Further processing in pythonOCC
- Advanced CAD operations
- Topology analysis

## Extending the Model

### Adding New Components

Create a new class inheriting from `BridgeComponent`:

```python
class Bearing(BridgeComponent):
    def __init__(self, width, height, length):
        super().__init__()
        self.width = width
        self.height = height
        self.length = length
    
    def create_geometry(self):
        bearing_shape = create_rectangular_prism(
            self.width, self.height, self.length
        )
        self.set_shape(bearing_shape)
```

### Modifying Girder Spacing

Adjust the spacing pattern in `compute_layout()` method for non-uniform spacing.

### Adding Deck Openings

Use Boolean subtraction operations in the `create_components()` method.

## Troubleshooting

### Display Issues

If the 3D viewer doesn't appear:
1. Check pythonOCC installation
2. Ensure display backend is available (requires GUI)
3. Try running in a different environment

### Export Failures

If export fails:
1. Check file write permissions
2. Verify output directory exists
3. Check pythonOCC version compatibility

### Import Errors

If you get import errors:
```bash
# Reinstall pythonOCC
conda install -c conda-forge pythonocc-core --force-reinstall
```

## Performance Notes

- **Large Models**: Increase number of girders or span length may impact performance
- **Skew Angle**: Rotation operations are computationally intensive
- **Export**: Large assemblies may take longer to export

## Known Limitations

1. Deck is modeled as single prism (no segmentation implemented)
2. No diaphragms or cross-bracing
3. Simplified parapet geometry
4. No bearing details
5. No connection details between components

## Future Enhancements

Potential improvements:

- [ ] Deck segmentation for better representation
- [ ] Diaphragms and cross-bracing
- [ ] Bearing details at supports
- [ ] Connection plates and bolts
- [ ] Varying girder sections along length
- [ ] Command-line interface for parameters
- [ ] Automated dimension validation
- [ ] Load analysis integration

## References

- [pythonOCC Documentation](https://github.com/tpaviot/pythonocc-core)
- [OpenCASCADE Technology](https://www.opencascade.com/)
- Steel Bridge Design Standards

## License

This project is created for educational purposes.

## Author

Bridge Model Generator
January 2026

## Acknowledgments

- Based on architecture specification in ARCH.txt
- Uses pythonOCC library by Thomas Paviot
- Component factory functions adapted from provided examples
