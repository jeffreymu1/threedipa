"""
Renderer module for haploscope display management.

This module provides classes and utilities for rendering stimuli on dual-monitor
haploscope setups using PsychoPy.
"""

from .haploscopeRender import (
    HaplscopeRender,
    HaplscopeRender2D,
    HaplscopeRender3D,
)
from .haploscopeConfig import (
    physical_calibration,
    monitor_settings,
)
from . import haplscope_utils

__all__ = [
    "HaplscopeRender",
    "HaplscopeRender2D",
    "HaplscopeRender3D",
    "physical_calibration",
    "monitor_settings",
    "haplscope_utils",
]

