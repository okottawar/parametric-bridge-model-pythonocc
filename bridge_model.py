import sys
import math

from OCC.Core.gp import gp_Vec, gp_Trsf, gp_Ax1, gp_Dir, gp_Pnt
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Core.BRep import BRep_Builder
from OCC.Core.TopoDS import TopoDS_Compound
from OCC.Display.SimpleGui import init_display
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCC.Core.BRepTools import breptools
from OCC.Extend.DataExchange import write_step_file


# Parameters
UNITS = "mm"
SPAN_LENGTH_L = 12000
N_GIRDERS = 3
GIRDER_CENTROID_SPACING = 3000
GIRDER_OFFSET_FROM_EDGE = 500
SKEW_ANGLE = 10

GIRDER_SECTION_D = 900
GIRDER_SECTION_BF = 300
GIRDER_SECTION_TF = 16
GIRDER_SECTION_TW = 10

DECK_THICKNESS = 200

PARAPET_WIDTH = 300
PARAPET_HEIGHT = 1000

SHOW_AXES = True
BACKGROUND_COLOR = "white"

SAVE_STEP = True
STEP_FILENAME = "bridge_model.step"
SAVE_BREP = True
BREP_FILENAME = "bridge_model.brep"

# Factory functions
# from draw_i_section import create_i_section as external_i_section
# from draw_rectangular_prism import create_rectangular_prism as external_prism

#Custom Implementation:
def create_i_section(d, bf, tf, tw, length):
    web_height = d - 2 * tf

    bottom_flange = BRepPrimAPI_MakeBox(length, bf, tf).Shape()

    top_flange = BRepPrimAPI_MakeBox(length, bf, tf).Shape()
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(0, 0, d - tf))
    top_flange = BRepBuilderAPI_Transform(top_flange, trsf, True).Shape()

    web = BRepPrimAPI_MakeBox(length, tw, web_height).Shape()
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(0, (bf - tw) / 2, tf))
    web = BRepBuilderAPI_Transform(web, trsf, True).Shape()

    shape = BRepAlgoAPI_Fuse(bottom_flange, top_flange).Shape()
    shape = BRepAlgoAPI_Fuse(shape, web).Shape()
    return shape

def create_rectangular_prism(width, height, length):
    return BRepPrimAPI_MakeBox(length, width, height).Shape()


# Base Class
class BridgeComponent:
    
    """
    Base class for all bridge components.

    Provides common functionality for managing OCC shapes and
    performing geometric transformations such as translation
    and rotation.
    """

    def __init__(self):
        self.shape = None

    def set_shape(self, s):
        self.shape = s

    def get_shape(self):
        return self.shape

    def translate(self, dx, dy, dz):

        """
        Translate the component in 3D space.

        Parameters
        ----------
        dx : float
            Translation distance along X-axis.
        dy : float
            Translation distance along Y-axis.
        dz : float
            Translation distance along Z-axis.
        """

        trsf = gp_Trsf()
        trsf.SetTranslation(gp_Vec(dx, dy, dz))
        self.shape = BRepBuilderAPI_Transform(self.shape, trsf, True).Shape()

    def rotate(self, axis_point, axis_direction, angle_deg):

        """
        Rotate the component about a specified axis.

        Parameters
        ----------
        axis_point : gp_Pnt
            A point on the axis of rotation.
        axis_direction : gp_Dir
            Direction vector defining the rotation axis.
        angle_deg : float
            Rotation angle in degrees.
        """

        axis = gp_Ax1(axis_point, axis_direction)
        trsf = gp_Trsf()
        trsf.SetRotation(axis, math.radians(angle_deg))
        self.shape = BRepBuilderAPI_Transform(self.shape, trsf, True).Shape()


# Component Classes
class Girder(BridgeComponent):
    
    """
    Represents a longitudinal steel girder modeled as an I-section.
    """

    def __init__(self, d, bf, tf, tw, length):
        super().__init__()
        self.d, self.bf, self.tf, self.tw, self.length = d, bf, tf, tw, length

    def create_geometry(self):
        self.set_shape(create_i_section(self.d, self.bf, self.tf, self.tw, self.length))


class Deck(BridgeComponent):
    
    """
    Represents the concrete deck slab of the bridge.
    """
    
    def __init__(self, width, thickness, length):
        super().__init__()
        self.width, self.thickness, self.length = width, thickness, length

    def create_geometry(self):
        self.set_shape(create_rectangular_prism(self.width, self.thickness, self.length))


class Parapet(BridgeComponent):
    
    """
    Represents a bridge parapet (edge safety barrier).
    """
    
    def __init__(self, width, height, length):
        super().__init__()
        self.width, self.height, self.length = width, height, length

    def create_geometry(self):
        self.set_shape(create_rectangular_prism(self.width, self.height, self.length))


# Bridge Model
class BridgeModel:
    
    """
    Parametric assembly of a short-span steel girder bridge.

    This class orchestrates:
    - Creation of components
    - Spatial positioning
    - Assembly of components
    - Visualization of assembly
    - Export to CAD formats (.STEP and .BREP)
    """

    def __init__(self, span_length, n_girders, spacing, overhang, skew_angle,
                 girder_section_d, girder_section_bf, girder_section_tf,
                 girder_section_tw, deck_thickness):

        self.span_length = span_length
        self.n_girders = n_girders
        self.spacing = spacing
        self.overhang = overhang
        self.skew_angle = skew_angle

        self.girder_section_d = girder_section_d
        self.girder_section_bf = girder_section_bf
        self.girder_section_tf = girder_section_tf
        self.girder_section_tw = girder_section_tw

        self.deck_thickness = deck_thickness

        self.girders = []
        self.parapets = []
        self.deck = None
        self.assembly_shape = None

    def compute_layout(self):
    
        """
        Compute derived geometric parameters for the bridge layout.

        Calculates:
        - Deck width based on girder spacing and overhang
        - Y-positions of girders
        - Deck elevation (Z-level)
        """

        self.deck_width = self.spacing * (self.n_girders - 1) + 2 * self.overhang
        start_y = -self.spacing * (self.n_girders - 1) / 2
        self.girder_positions_y = [start_y + i * self.spacing for i in range(self.n_girders)]
        self.deck_z_level = self.girder_section_d

    def create_components(self):
        
        """
        Instantiate all bridge components (girders, deck, parapets)
        using parametric dimensions.
        """
        
        for y in self.girder_positions_y:
            g = Girder(self.girder_section_d, self.girder_section_bf,
                       self.girder_section_tf, self.girder_section_tw, self.span_length)
            g.create_geometry()
            self.girders.append(g)

        self.deck = Deck(self.deck_width, self.deck_thickness, self.span_length)
        self.deck.create_geometry()

        for _ in range(2):
            p = Parapet(PARAPET_WIDTH, PARAPET_HEIGHT, self.span_length)
            p.create_geometry()
            self.parapets.append(p)

    def position_components(self):
        
        """
        Apply translations to correctly place each component in 3D space
        according to the computed layout.
        """
        
        for g, y in zip(self.girders, self.girder_positions_y):
            g.translate(0, y, 0)

        self.deck.translate(0, -self.deck_width / 2, self.deck_z_level)

        parapet_z = self.deck_z_level + self.deck_thickness
        half_w = self.deck_width / 2
        self.parapets[0].translate(0, -half_w - PARAPET_WIDTH / 2, parapet_z)
        self.parapets[1].translate(0, half_w - PARAPET_WIDTH / 2, parapet_z)

    def assemble(self):
        
        """
        Combine all component shapes into a single TopoDS_Compound
        representing the complete bridge assembly.
        """
        
        builder = BRep_Builder()
        compound = TopoDS_Compound()
        builder.MakeCompound(compound)

        for g in self.girders:
            builder.Add(compound, g.get_shape())
        builder.Add(compound, self.deck.get_shape())
        for p in self.parapets:
            builder.Add(compound, p.get_shape())

        self.assembly_shape = compound

    def display(self):
        
        """
        Launch the OCC 3D viewer and render the assembled bridge model
        with color-coded components and optional axes.
        """

        display, start_display, *_ = init_display()

        view = display.View

        if BACKGROUND_COLOR == "white":
            view.SetBackgroundColor(Quantity_Color(1.0, 1.0, 1.0, Quantity_TOC_RGB))
        else:
            view.SetBackgroundColor(Quantity_Color(0.5, 0.5, 0.5, Quantity_TOC_RGB))

        if SHOW_AXES:
            display.display_triedron()
        
        for g in self.girders:
            display.DisplayShape(g.get_shape(), color=Quantity_Color(0.7,0.7,0.75,Quantity_TOC_RGB))

        display.DisplayShape(self.deck.get_shape(), color=Quantity_Color(0.8,0.8,0.8,Quantity_TOC_RGB))

        for p in self.parapets:
            display.DisplayShape(p.get_shape(), color=Quantity_Color(0.9,0.9,0.85,Quantity_TOC_RGB))

        display.FitAll()
        start_display()

    def export(self):
        
        """
        Export the bridge assembly to CAD formats.

        Exports:
        - STEP file (if SAVE_STEP is True)
        - BREP file (if SAVE_BREP is True)
        """
        
        if SAVE_STEP:
            print(f"Exporting STEP file: {STEP_FILENAME}")
            write_step_file(self.assembly_shape, STEP_FILENAME)

        if SAVE_BREP:
            print(f"Exporting BREP file: {BREP_FILENAME}")
            breptools.Write(self.assembly_shape, BREP_FILENAME)

# Main Function - entry point
def main():
    
    """
    Entry point of the program.

    Creates the bridge model, builds the geometry, assembles
    components, optionally exports files, and opens the 3D viewer.
    """
    
    bridge = BridgeModel(
        SPAN_LENGTH_L, N_GIRDERS, GIRDER_CENTROID_SPACING,
        GIRDER_OFFSET_FROM_EDGE, SKEW_ANGLE,
        GIRDER_SECTION_D, GIRDER_SECTION_BF,
        GIRDER_SECTION_TF, GIRDER_SECTION_TW,
        DECK_THICKNESS
    )

    bridge.compute_layout()
    bridge.create_components()
    bridge.position_components()
    bridge.assemble()
    bridge.display()
    bridge.export()


if __name__ == "__main__":
    main()
