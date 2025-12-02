"""
Haploscope setup and management for dual-monitor stereoscopic displays.

This module provides functions to create and manage two PsychoPy windows
on separate monitors for haploscope-based depth perception experiments.
"""
#Core libraries
import math

#Third party libraries
import numpy as np
from psychopy import visual, monitors
from pathlib import Path

#Local libraries
from . import haploscopeConfig as config

#------------------------------------------------------------------------------
# Physical calibration functions
#------------------------------------------------------------------------------
def calc_display_positions(
    focal_distance: float
    ) -> tuple[float, float]:
    """Return the left/right display carriage positions for ``focal_distance``.

    Parameters
    ----------
    focal_distance:
        Requested distance from the mirrors to the focal plane in millimetres.

    Returns
    -------
    tuple
        (left_position, right_position) in the millimeters.
    """

    distance_change = abs(focal_distance) - config["MIN_FOCAL_DISTANCE"]
    left_pos = config["DISPLAY_LEFT_ZERO"] - distance_change
    right_pos = config["DISPLAY_RIGHT_ZERO"] + distance_change
    return left_pos, right_pos


def calc_eye_positions(
    iod: float
    ) -> tuple[float, float]:
    """Return mirror eye positions for a given interpupillary distance."""

    distance_change = (abs(iod) - config["MIN_IOD"]) / 2.0
    left_pos = config["EYE_LEFT_ZERO"] - distance_change
    right_pos = config["EYE_RIGHT_ZERO"] + distance_change
    return left_pos, right_pos


def calc_arm_rotations(iod: float, focal_distance: float) -> float:
    """Return the mirror arm rotation angle in degrees.
    """

    angle_rad = math.atan(0.5 * iod / focal_distance)
    return math.degrees(angle_rad)


def calc_physical_calibration(
    iod: float,
    focal_distance: float,
    config: dict[str, float]
    ) -> dict[str, float]:
    """Return a dict summarising all physical calibration values.
    """

    display_left, display_right = calc_display_positions(focal_distance, config)
    eye_left, eye_right = calc_eye_positions(iod, config)
    angle = calc_arm_rotations(iod, focal_distance)
    return {
        "DISPLAY_LEFT": display_left,
        "DISPLAY_RIGHT": display_right,
        "EYE_LEFT": eye_left,
        "EYE_RIGHT": eye_right,
        "ANGLE": angle,
    }


#------------------------------------------------------------------------------
# Window setup functions
#------------------------------------------------------------------------------
def setup_haploscope_windows(
    monitor_names: tuple[str, str] = ("left", "right"),
    screen_indices: tuple[int, int] = (0, 1),
    size_pix: tuple[int, int] = [],
    fullscr: bool = True,
    color: tuple[float, float, float] = (-1, -1, -1),
    waitBlanking: bool = True,
    **kwargs
) -> tuple[visual.Window, visual.Window]:
    """
    Set up two PsychoPy windows on separate monitors for haploscope display.
    
    Parameters
    ----------
    monitor_names : tuple of str, optional
        Names of the monitor configurations (default: ("left", "right"))
        These should match monitor names in PsychoPy Monitor Center.
    screen_indices : tuple of int, optional
        Which physical screens to use (default: (0, 1))
        0 is typically the primary display, 1 is the secondary.
    size_pix : tuple[int, int], optional
        Window size in pixels. If None, uses full screen size.
    fullscr : bool, optional
        Whether to use fullscreen mode (default: True)
    color : tuple[float, float, float], optional
        Background color (default: (-1, -1, -1) for black in PsychoPy's -1 to 1 color space)
    waitBlanking : bool, optional
        Whether to wait for vertical blank before flipping (default: True)
        Set to False on one window if you want to control sync manually.
    **kwargs
        Additional arguments passed to visual.Window constructor
        
    Returns
    -------
    tuple of visual.Window
        (left_window, right_window) - Two PsychoPy window objects
        
    Examples
    --------
    >>> left_win, right_win = setup_haploscope_windows(
    ...     monitor_names=("left_monitor", "right_monitor"),
    ...     screen_indices=(0, 1)
    ... )
    """
    left_monitor, right_monitor = monitor_names
    left_screen, right_screen = screen_indices

    if size_pix == []:
        size_pix = (800, 600)
        fullscr = False
        print("Using default size (800x600) for non-fullscreen mode")
    # Create left window
    left_window = visual.Window(
        size=size_pix,
        screen=left_screen,
        fullscr=fullscr,
        monitor=left_monitor,
        color=color,
        waitBlanking=waitBlanking,
        **kwargs
    )
    
    # Create right window
    right_window = visual.Window(
        size=size_pix,
        screen=right_screen,
        fullscr=fullscr,
        monitor=right_monitor,
        color=color,
        waitBlanking=waitBlanking,
        **kwargs
    )
    
    return left_window, right_window


def update_window_image(
    window: visual.Window,
    image: str ,
    position: tuple[float, float] = (0, 0),
    size: tuple[float, float] = [],
    flip: bool = True
) -> visual.ImageStim:
    """
    Create and display an image on a PsychoPy window.
    
    Parameters
    ----------
    window : visual.Window
        The PsychoPy window to display the image on
    image : str, Path, or numpy.ndarray
        Path to image file or numpy array of image data
    position : tuple[float, float], optional
        (x, y) position in window coordinates (default: (0, 0))
    size : tuple[float, float], optional
        (width, height) size in window coordinates. If None, uses image size.
    flip : bool, optional
        Whether to flip the window after drawing (default: True)
        
    Returns
    -------
    visual.ImageStim
        The image stimulus object (can be reused/modified)
        
    Examples
    --------
    >>> img_stim = update_window_image(
    ...     left_win, 
    ...     "path/to/image.png",
    ...     position=(0, 0)
    ... )
    """
    image_stim = visual.ImageStim(
        win=window,
        image=image,
        pos=position,
        size=size
    )
    
    image_stim.draw()
    
    if flip:
        window.flip()
    
    return image_stim


def update_both_windows(
    left_window: visual.Window,
    right_window: visual.Window,
    left_image: str,
    right_image: str,
    left_position: tuple[float, float] = (0, 0),
    right_position: tuple[float, float] = (0, 0),
    left_size: tuple[float, float] = [],
    right_size: tuple[float, float] = [],
    sync_flip: bool = True
) -> tuple[visual.ImageStim, visual.ImageStim]:
    """
    Update both haploscope windows with separate images simultaneously.
    
    Parameters
    ----------
    left_window : visual.Window
        Left monitor window
    right_window : visual.Window
        Right monitor window
    left_image : str
        Image to display on left window
    right_image : str
        Image to display on right window
    left_position : tuple of float, optional
        Position for left image (default: (0, 0))
    right_position : tuple of float, optional
        Position for right image (default: (0, 0))
    left_size : tuple[float, float] = [], optional
        Size for left image (default: [], uses image size)
    right_size : tuple of float = [], optional
        Size for right image (default: [], uses image size)
    sync_flip : bool, optional
        Whether to synchronize the flip of both windows (default: True)
        If True, draws both then flips both. If False, flips each as drawn.
        
    Returns
    -------
    tuple of visual.ImageStim
        (left_stim, right_stim) - Image stimulus objects for both windows
        
    Examples
    --------
    >>> left_stim, right_stim = update_both_windows(
    ...     left_win, right_win,
    ...     "left_stimulus.png",
    ...     "right_stimulus.png"
    ... )
    """
    # Create image stimuli
    left_stim = visual.ImageStim(
        win=left_window,
        image=left_image,
        pos=left_position,
        size=left_size
    )
    
    right_stim = visual.ImageStim(
        win=right_window,
        image=right_image,
        pos=right_position,
        size=right_size
    )
    
    # Draw both images
    left_stim.draw()
    right_stim.draw()
    
    # Flip windows (synchronized or separate)
    if sync_flip:
        # Draw both first, then flip both for synchronization
        left_window.flip()
        right_window.flip()
    else:
        # Flip each as drawn (may have slight timing differences)
        left_window.flip()
        right_window.flip()
    
    return left_stim, right_stim


def close_haploscope_windows(
    left_window: visual.Window,
    right_window: visual.Window
) -> None:
    """
    Close both haploscope windows cleanly.
    
    Parameters
    ----------
    left_window : visual.Window
        Left monitor window to close
    right_window : visual.Window
        Right monitor window to close
    """
    left_window.close()
    right_window.close()


def get_monitor_info(screen_index: int) -> dict:
    """
    Get information about a specific monitor.
    
    Parameters
    ----------
    screen_index : int
        Index of the monitor (0 = primary, 1 = secondary, etc.)
        
    Returns
    -------
    dict
        Dictionary containing monitor information (size, resolution, etc.)
    """
    # Get all monitors
    all_monitors = monitors.getAllMonitors()
    
    if screen_index >= len(all_monitors):
        raise ValueError(f"Screen index {screen_index} not available. "
                        f"Found {len(all_monitors)} monitor(s).")
    
    monitor = monitors.Monitor(all_monitors[screen_index])
    
    return {
        'name': all_monitors[screen_index],
        'size': monitor.getSizePix(),
        'width': monitor.getWidth(),
        'distance': monitor.getDistance(),
    }