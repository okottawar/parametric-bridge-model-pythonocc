# PARAMETRIC 3D CAD MODEL OF A STEEL GIRDER BRIDGE

**Implementation Documentation**

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Project Overview](#project-overview)
3. [Architecture and Design](#architecture-and-design)
4. [Implementation Details](#implementation-details)
5. [Code Walkthrough](#code-walkthrough)
6. [Usage Guide](#usage-guide)
7. [Testing and Validation](#testing-and-validation)
8. [Deliverables](#deliverables)
[Appendix](#appendix)
---

## 1. Executive Summary

This document describes the implementation of a parametric 3D CAD model of a steel girder bridge superstructure using the pythonOCC library. The solution provides a modular, object-oriented framework for creating customizable bridge models with adjustable parameters.

### Key Features

- **Component-based architecture** following the provided ARCH.txt specification
- **Parametric design** allowing complete customization of bridge dimensions
- **Support for multiple girders**, adjustable deck dimensions, and parapets
- **Optional skew angle** implementation (0-15 degrees)
- **Interactive 3D visualization** with color-coded components
- **Export capabilities** to STEP and BREP file formats

---

## 2. Project Overview

### 2.1 Problem Statement

The objective was to create a parametric, modular 3D CAD model of a short-span steel girder bridge using pythonOCC. The model needed to be assembled from component factories with adjustable parameters, providing a complete, runnable script that builds, visualizes, and exports bridge geometry.

### 2.2 Bridge Components

The bridge model consists of three primary components:

1. **Main Longitudinal Steel Girders (I-sections)**: The primary structural elements that span the length of the bridge. Each girder is modeled as an I-section with parametric dimensions including depth, flange width, flange thickness, and web thickness.

2. **Concrete Deck Slab**: A rectangular prism representing the bridge deck that sits on top of the girders. The deck width is automatically calculated based on girder spacing and overhang parameters.

3. **Parapets**: Safety barriers positioned on both sides of the bridge deck, modeled as rectangular prisms with adjustable width and height.

---

## 3. Architecture and Design

### 3.1 Class Hierarchy

The implementation follows an object-oriented design with a clear class hierarchy:

| Class | Role | Key Methods |
|-------|------|-------------|
| **BridgeComponent** | Base class for all components | `set_shape()`, `get_shape()`, `translate()`, `rotate()` |
| **Girder** | I-section steel girder | `create_geometry()` |
| **Deck** | Concrete deck slab | `create_geometry()` |
| **Parapet** | Safety barrier | `create_geometry()` |
| **BridgeModel** | Complete bridge assembly | `compute_layout()`, `create_components()`, `position_components()`, `assemble()`, `display()`, `export()` |

### 3.2 Design Patterns

The implementation uses several design patterns:

- **Factory Pattern**: Component creation is handled by factory functions (`create_i_section`, `create_rectangular_prism`) that return TopoDS shapes.

- **Template Method Pattern**: The BridgeModel class defines a workflow (`compute_layout` → `create_components` → `position_components` → `assemble`) that is executed in sequence.

- **Composite Pattern**: Individual components are assembled into a compound shape representing the complete bridge.

### 3.3 Architecture 

```
BridgeComponent (Base Class)
├── set_shape()
├── get_shape()
├── translate(dx, dy, dz)
└── rotate(axis, angle)

Girder (extends BridgeComponent)
├── Attributes: d, bf, tf, tw, length
└── create_geometry()

Deck (extends BridgeComponent)
├── Attributes: width, thickness, length
└── create_geometry()

Parapet (extends BridgeComponent)
├── Attributes: width, height, length
└── create_geometry()

BridgeModel (Assembly Class)
├── compute_layout()
├── create_components()
├── position_components()
├── assemble()
├── display()
└── export()
```

---

## 4. Implementation Details

### 4.1 Parameters

All bridge dimensions are exposed as global parameters at the top of the script, allowing easy customization:

| Parameter | Default Value | Description |
|-----------|---------------|-------------|
| `SPAN_LENGTH_L` | 12000 mm | Total clear span length |
| `N_GIRDERS` | 3 | Number of main girders |
| `GIRDER_CENTROID_SPACING` | 3000 mm | Center-to-center girder spacing |
| `GIRDER_OFFSET_FROM_EDGE` | 500 mm | Deck overhang |
| `SKEW_ANGLE` | 10° | Bridge skew angle |
| `GIRDER_SECTION_D` | 900 mm | I-section depth |
| `GIRDER_SECTION_BF` | 300 mm | I-section flange width |
| `GIRDER_SECTION_TF` | 16 mm | Flange thickness |
| `GIRDER_SECTION_TW` | 10 mm | Web thickness |
| `DECK_THICKNESS` | 200 mm | Deck slab thickness |
| `PARAPET_WIDTH` | 300 mm | Parapet width |
| `PARAPET_HEIGHT` | 1000 mm | Parapet height |

### 4.2 Coordinate System

The model uses a standard 3D coordinate system:

- **X-axis**: Longitudinal direction (along bridge span)
- **Y-axis**: Transverse direction (across bridge width)
- **Z-axis**: Vertical direction (height)

Girders are positioned symmetrically about the Y-axis origin, with the deck centered on the girders and parapets placed at the deck edges.

### 4.3 Derived Calculations

The `compute_layout()` method automatically calculates:

1. **Deck Width**: `deck_width = spacing × (n_girders - 1) + 2 × overhang`
2. **Girder Y-Positions**: Calculated to center the girder array about Y=0
3. **Deck Z-Level**: Set to `girder_section_d` (top of girders)

---

## 5. Code Walkthrough

### 5.1 Component Factory Functions

#### create_i_section()

Creates I-beam geometry by combining three rectangular boxes:
1. Bottom flange
2. Web (centered vertically)
3. Top flange

The function uses `BRepAlgoAPI_Fuse` to combine the components into a single solid.

```python
def create_i_section(d, bf, tf, tw, length):
    web_height = d - 2 * tf
    bottom_flange = BRepPrimAPI_MakeBox(length, bf, tf).Shape()
    # ... positioning and fusion operations
    return i_section_solid
```

#### create_rectangular_prism()

Simple wrapper around `BRepPrimAPI_MakeBox` for creating rectangular prisms.

### 5.2 BridgeComponent Base Class

Provides common functionality for all bridge components:

- **Shape Management**: `set_shape()` and `get_shape()` methods
- **Translation**: Uses `gp_Vec` and `gp_Trsf` for 3D translation
- **Rotation**: Uses `gp_Ax1` for rotation around an arbitrary axis

### 5.3 Component Classes

Each component class inherits from `BridgeComponent` and implements:

- Constructor to store parameters
- `create_geometry()` method to build the 3D shape

### 5.4 BridgeModel Class

#### compute_layout()

Calculates all derived geometric parameters based on input parameters.

#### create_components()

Instantiates all bridge components:
- Creates N girders based on `n_girders` parameter
- Creates single deck slab
- Creates left and right parapets

#### position_components()

Places components in 3D space:
1. Translates girders to calculated Y-positions
2. Positions deck on top of girders
3. Places parapets at deck edges
4. Applies skew rotation if specified

#### assemble()

Uses `BRepBuilderAPI_MakeCompound` to create a single compound shape containing all components.

#### display()

Initializes OCC 3D viewer with:
- Color-coded components (steel gray for girders, concrete gray for deck)
- Configurable background color
- Automatic fit-to-view

#### export()

Exports assembly to STEP and/or BREP formats using pythonOCC's data exchange functions.

---

## 6. Usage Guide

### 6.1 Installation

#### Prerequisites

- Python 3.7 or higher
- pythonOCC-core library

#### Install pythonOCC

```bash
# Using conda (recommended)
conda install -c conda-forge pythonocc-core

# OR using pip
pip install pythonocc-core
```

### 6.2 Basic Usage

Run the bridge model with default parameters:

```bash
python bridge_model.py
```

This will:
1. Create the bridge model
2. Display it in an interactive 3D viewer
3. Optionally export to files (if enabled)

### 6.3 Customizing Parameters

Edit parameters at the top of `bridge_model.py`:

```python
# Example: Create a wider bridge with 4 girders
N_GIRDERS = 4
GIRDER_CENTROID_SPACING = 2500
SPAN_LENGTH_L = 15000
```

### 6.4 Exporting Models

Enable export by setting flags:

```python
SAVE_STEP = True
STEP_FILENAME = "my_bridge.step"

SAVE_BREP = True
BREP_FILENAME = "my_bridge.brep"
```

STEP files can be imported into:
- AutoCAD
- SolidWorks
- CATIA
- Most other CAD software

### 6.5 Visualization Controls

In the 3D viewer:
- **Rotate**: Click and drag with left mouse button
- **Zoom**: Mouse wheel or pinch gesture
- **Pan**: Click and drag with right mouse button
- **Close**: Close window to continue script execution

---

## 7. Testing and Validation

### 7.1 Test Suite

The `test_bridge_model.py` script provides comprehensive testing:

1. **Component Creation Tests**: Verify that all component types can be instantiated
2. **Transformation Tests**: Ensure translation and rotation operations work correctly
3. **Configuration Tests**: Validate multiple bridge configurations
4. **Parameter Validation Tests**: Check edge cases and boundary conditions

### 7.2 Test Configurations

The implementation has been validated with:

| Configuration | Span | Girders | Spacing | Skew |
|---------------|------|---------|---------|------|
| Default | 12m | 3 | 3000mm | 10° |
| Medium | 15m | 4 | 2500mm | 0° |
| Wide | 20m | 5 | 3500mm | 15° |

### 7.3 Running Tests

```bash
python test_bridge_model.py
```

Expected output:
```
==========================================
BRIDGE MODEL TEST SUITE
==========================================

TEST 1: Component Creation
✓ Girder created successfully
✓ Deck created successfully
✓ Parapet created successfully

TEST 2: Component Transformations
✓ Translation successful
✓ Rotation successful

...

ALL TESTS PASSED! ✓
```

---

## 8. Deliverables

The complete project includes:

1. **bridge_model.py** - Main implementation script (complete solution)
2. **test_bridge_model.py** - Comprehensive test suite
3. **draw_i_section.py** and **draw_rectangular_prism.py** - component factory functions
4. **README.md** - User documentation and usage guide
5. **requirements.txt** - Python dependencies
6. **Documentation.md** - Technical documentation and code walkthrough

All files are ready for submission and can be packaged as required.

---

## Appendix A: File Compatibility

### Compatibility with Provided Files

The solution is fully compatible with the provided files:

- **draw_i_section.py**: The `create_i_section()` function follows the same pattern but adapts parameter naming to match the problem specification (d, bf, tf, tw instead of width, depth, etc.)

- **draw_rectangular_prism.py**: The `create_rectangular_prism()` function is directly compatible and uses the same approach

- **portal_frame.py**: Demonstrates similar usage patterns with pythonOCC that are applied in the bridge model

- **ARCH.txt**: Complete implementation of the specified architecture

### Import Compatibility

If needed, the provided factory functions can be imported directly:

```python
from draw_i_section import create_i_section as external_i_section
from draw_rectangular_prism import create_rectangular_prism as external_prism
```

---

## Appendix B: Parameter Reference

Complete parameter reference with units and constraints:

| Parameter | Type | Unit | Range | Default |
|-----------|------|------|-------|---------|
| UNITS | string | - | "mm" or "m" | "mm" |
| SPAN_LENGTH_L | float | mm | > 0 | 12000 |
| N_GIRDERS | int | - | ≥ 3 | 3 |
| GIRDER_CENTROID_SPACING | float | mm | > 0 | 3000 |
| GIRDER_OFFSET_FROM_EDGE | float | mm | ≥ 0 | 500 |
| SKEW_ANGLE | float | degrees | 0-15 | 10 |
| GIRDER_SECTION_D | float | mm | > 0 | 900 |
| GIRDER_SECTION_BF | float | mm | > 0 | 300 |
| GIRDER_SECTION_TF | float | mm | > 0, < D/2 | 16 |
| GIRDER_SECTION_TW | float | mm | > 0, < BF | 10 |
| DECK_THICKNESS | float | mm | > 0 | 200 |
| PARAPET_WIDTH | float | mm | > 0 | 300 |
| PARAPET_HEIGHT | float | mm | > 0 | 1000 |

---

**End of Documentation**
