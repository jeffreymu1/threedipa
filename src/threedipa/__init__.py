"""
vizlab3d: A package for 3D vision psychology experiments using PsychoPy

This package provides tools for creating stereoscopic vision experiments
using haploscope displays and PsychoPy.

Usage:
    Import submodules to access functionality:
    
    >>> from threedipa.renderer import HaplscopeRender2D
    >>> from threedipa.stimuli import Stimulus2DImage
    >>> import threedipa.utils as utils
"""

__version__ = "0.0.1"

# Expose submodules for direct import
from . import renderer
from . import stimuli
from . import utils
from . import procedure
from . import monitor_calibration
from . import config
from . import initVariables

__all__ = [
    "__version__",
    "renderer",
    "stimuli",
    "utils",
    "procedure",
    "monitor_calibration",
    "config",
    "initVariables",
]
