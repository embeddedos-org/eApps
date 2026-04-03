"""EoStudio editor panels — one per design domain."""

from eostudio.gui.editors.modeler_3d import Modeler3DEditor
from eostudio.gui.editors.cad_editor import CADEditor
from eostudio.gui.editors.image_editor import ImageEditor
from eostudio.gui.editors.game_editor import GameEditor
from eostudio.gui.editors.ui_designer import UIDesigner
from eostudio.gui.editors.product_designer import ProductDesigner
from eostudio.gui.editors.interior_editor import InteriorEditor
from eostudio.gui.editors.uml_editor import UMLEditor
from eostudio.gui.editors.simulation_editor import SimulationEditor
from eostudio.gui.editors.database_editor import DatabaseEditor
from eostudio.gui.editors.ide_editor import IDEEditor

__all__ = [
    "Modeler3DEditor",
    "CADEditor",
    "ImageEditor",
    "GameEditor",
    "UIDesigner",
    "ProductDesigner",
    "InteriorEditor",
    "UMLEditor",
    "SimulationEditor",
    "DatabaseEditor",
    "IDEEditor",
]
