"""
Stimuli module for 2D stereoscopic stimulus management.

This module provides classes for loading and managing 2D image stimuli
for stereoscopic display on haploscopes.
"""

from .stimulus2D import (
    Stimulus2D,
    Stimulus2DImage,
    Stimulus2DImageSequence,
)
from .stimuli import make_fixation_cross

__all__ = [
    "Stimulus2D",
    "Stimulus2DImage",
    "Stimulus2DImageSequence",
    "make_fixation_cross",
]

