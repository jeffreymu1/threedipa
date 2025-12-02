"""
Monitor calibration functions for haploscope setups.

This module provides functions to configure monitor information, calibrate
gamma tables, and manage screen center coordinates for accurate stimulus
presentation in depth perception experiments.
"""

from typing import Optional, Tuple, Union, List, Dict
import numpy as np
from pathlib import Path
from psychopy import monitors
from psychopy.visual import Window

def get_monitor_configuration(
    size_pix: tuple[int, int],
    size_cm: tuple[float, float],
) -> dict:
    """
    Get monitor configuration information.
    
    Parameters
    ----------
    monitor_name: str
        Name of the monitor to get configuration information for
    """
    mon = monitors.Monitor(monitor_name)


def set_monitor_info(
    name: str,
    width_cm: float,
    distance_cm: float,
    size_pix: Tuple[int, int],
    gamma: Optional[Union[float, Tuple[float, float, float]]] = None,
    center_offset_pix: Optional[Tuple[int, int]] = None
) -> monitors.Monitor:
    """
    Set and save monitor information in PsychoPy's Monitor Center.
    
    Parameters
    ----------
    name : str
        Unique name for the monitor configuration
    width_cm : float
        Physical width of the monitor in centimeters
    distance_cm : float
        Distance from observer to monitor in centimeters
    size_pix : tuple of (width, height)
        Screen resolution in pixels
    gamma : float or tuple of (r, g, b), optional
        Gamma value(s) for the monitor. If single float, applied to all channels.
        If tuple, separate gamma for R, G, B channels.
    center_offset_pix : tuple of (x, y), optional
        Offset from physical center to logical center in pixels.
        This is useful if the optical center differs from pixel center.
        
    Returns
    -------
    monitors.Monitor
        The configured Monitor object
        
    Examples
    --------
    """
    mon = monitors.Monitor(name)
    mon.setWidth(width_cm)
    mon.setDistance(distance_cm)
    mon.setSizePix(size_pix)
    
    if gamma is not None:
        if isinstance(gamma, (int, float)):
            mon.setGamma(gamma)
        elif isinstance(gamma, (tuple, list)) and len(gamma) == 3:
            # Set gamma for each color channel separately
            mon.setGamma(gamma)
        else:
            raise ValueError("gamma must be a float or tuple of 3 floats (R, G, B)")
    
    if center_offset_pix is not None:
        # Store center offset as a custom attribute if needed
        # PsychoPy doesn't have a built-in method for this, so we'll handle it separately
        pass
    
    mon.save()
    return mon


def calibrate_gamma_table(
    monitor_name: str,
    measurements: Dict[str, Tuple[np.ndarray, np.ndarray]],
    method: str = "simple"
) -> monitors.Monitor:
    """
    Calibrate gamma table from luminance measurements.
    
    Parameters
    ----------
    monitor_name : str
        Name of the monitor to calibrate
    measurements : dict
        Dictionary with keys 'R', 'G', 'B' (or 'all') mapping to tuples of
        (intensities, luminances) where:
        - intensities: array of input intensity values (0-1 or 0-255)
        - luminances: array of measured luminance values (in cd/m²)
    method : str, optional
        Calibration method: 'simple' (single gamma value) or 'full' (full lookup table)
        (default: 'simple')
        
    Returns
    -------
    monitors.Monitor
        The calibrated Monitor object
        
    Examples
    --------
    >>> # Simple gamma calibration
    >>> intensities = np.linspace(0, 1, 11)
    >>> luminances = np.array([0.5, 2.1, 5.3, 10.2, 18.5, 30.1, 45.8, 65.2, 88.5, 115.2, 145.0])
    >>> measurements = {'all': (intensities, luminances)}
    >>> mon = calibrate_gamma_table("left_monitor", measurements)
    
    >>> # Separate RGB calibration
    >>> measurements = {
    ...     'R': (intensities, r_luminances),
    ...     'G': (intensities, g_luminances),
    ...     'B': (intensities, b_luminances)
    ... }
    >>> mon = calibrate_gamma_table("left_monitor", measurements, method='full')
    """
    mon = monitors.Monitor(monitor_name)
    
    if method == "simple":
        # Fit a simple power-law gamma function
        if 'all' in measurements:
            intensities, luminances = measurements['all']
            gamma = _fit_gamma(intensities, luminances)
            mon.setGamma(gamma)
        else:
            # Fit gamma for each channel
            gammas = []
            for channel in ['R', 'G', 'B']:
                if channel in measurements:
                    intensities, luminances = measurements[channel]
                    gamma = _fit_gamma(intensities, luminances)
                    gammas.append(gamma)
                else:
                    gammas.append(2.2)  # Default gamma
            mon.setGamma(tuple(gammas))
    
    elif method == "full":
        # Create full gamma lookup table (256 levels)
        gamma_grid = []
        
        for channel in ['R', 'G', 'B']:
            if channel in measurements:
                intensities, luminances = measurements[channel]
                lut = _create_gamma_lut(intensities, luminances)
                gamma_grid.append(lut)
            elif 'all' in measurements:
                intensities, luminances = measurements['all']
                lut = _create_gamma_lut(intensities, luminances)
                gamma_grid.append(lut)
            else:
                # Default linear lookup table
                gamma_grid.append(np.linspace(0, 1, 256))
        
        if len(gamma_grid) > 0:
            mon.setGammaGrid(gamma_grid)
    
    mon.save()
    return mon


def _fit_gamma(
    intensities: np.ndarray,
    luminances: np.ndarray,
    min_lum: Optional[float] = None
) -> float:
    """
    Fit a gamma function to luminance measurements.
    
    Fits: L = a + (b + k*V)^gamma
    Simplified: L = k*V^gamma (assuming a=0, b=0)
    
    Parameters
    ----------
    intensities : np.ndarray
        Input intensity values (0-1 or 0-255)
    luminances : np.ndarray
        Measured luminance values
    min_lum : float, optional
        Minimum luminance (black level). If None, uses minimum measured value.
        
    Returns
    -------
    float
        Estimated gamma value
    """
    # Normalize intensities to 0-1 range
    if intensities.max() > 1.0:
        intensities = intensities.astype(float) / 255.0
    
    # Normalize luminances
    max_lum = luminances.max()
    if min_lum is None:
        min_lum = luminances.min()
    
    # Subtract black level
    luminances_norm = (luminances - min_lum) / (max_lum - min_lum + 1e-10)
    
    # Avoid log(0)
    intensities_log = np.log(intensities + 1e-10)
    luminances_log = np.log(luminances_norm + 1e-10)
    
    # Filter out invalid values
    valid = (intensities > 1e-5) & (luminances_norm > 1e-5)
    if valid.sum() < 2:
        return 2.2  # Default gamma
    
    # Linear regression: log(L) = gamma * log(V)
    gamma, _ = np.polyfit(intensities_log[valid], luminances_log[valid], 1)
    
    # Ensure reasonable gamma range
    gamma = np.clip(gamma, 1.0, 5.0)
    
    return float(gamma)


def _create_gamma_lut(
    intensities: np.ndarray,
    luminances: np.ndarray,
    n_levels: int = 256
) -> np.ndarray:
    """
    Create a full gamma lookup table from measurements.
    
    Parameters
    ----------
    intensities : np.ndarray
        Input intensity values
    luminances : np.ndarray
        Measured luminance values
    n_levels : int, optional
        Number of levels in the lookup table (default: 256)
        
    Returns
    -------
    np.ndarray
        Lookup table array of shape (n_levels,)
    """
    # Normalize intensities to 0-1
    if intensities.max() > 1.0:
        intensities = intensities.astype(float) / 255.0
    
    # Normalize luminances to 0-1
    min_lum = luminances.min()
    max_lum = luminances.max()
    luminances_norm = (luminances - min_lum) / (max_lum - min_lum + 1e-10)
    
    # Create output levels
    output_levels = np.linspace(0, 1, n_levels)
    
    # Interpolate to create lookup table
    # We need to invert: given desired output luminance, what input intensity?
    # Sort by luminance for interpolation
    sort_idx = np.argsort(luminances_norm)
    lut = np.interp(output_levels, luminances_norm[sort_idx], intensities[sort_idx])
    
    # Ensure monotonic increase
    for i in range(1, len(lut)):
        if lut[i] < lut[i-1]:
            lut[i] = lut[i-1]
    
    return lut


def load_gamma_table(
    monitor_name: str,
    window: Optional[Window] = None
) -> Union[monitors.Monitor, Tuple[monitors.Monitor, Window]]:
    """
    Load gamma table from a saved monitor configuration.
    
    Parameters
    ----------
    monitor_name : str
        Name of the monitor configuration to load
    window : Window, optional
        If provided, applies gamma to the window. Otherwise returns monitor only.
        
    Returns
    -------
    monitors.Monitor or tuple
        If window is None, returns Monitor object.
        If window is provided, returns (Monitor, Window) tuple.
        
    Examples
    --------
    >>> # Load monitor configuration
    >>> mon = load_gamma_table("left_monitor")
    
    >>> # Load and apply to window
    >>> from psychopy import visual
    >>> win = visual.Window(monitor=mon)
    >>> mon, win = load_gamma_table("left_monitor", win)
    """
    mon = monitors.Monitor(monitor_name)
    
    if window is not None:
        # Apply gamma to window
        gamma = mon.getGamma()
        if gamma is not None:
            window.gamma = gamma
        
        # Apply gamma grid if available
        gamma_grid = mon.getGammaGrid()
        if gamma_grid is not None:
            window.gammaGrid = gamma_grid
        
        return mon, window
    
    return mon


def set_screen_center(
    size_pix: Tuple[int, int],
    center_offset_pix: Tuple[int, int] = (0, 0)
) -> Tuple[int, int]:
    """
    Calculate screen center coordinates in pixels.
    
    Parameters
    ----------
    size_pix : tuple of (width, height)
        Screen resolution in pixels
    center_offset_pix : tuple of (x, y), optional
        Offset from physical center to logical center in pixels.
        Useful for haploscope setups where optical center may differ from
        pixel center due to mirrors/prisms (default: (0, 0))
        
    Returns
    -------
    tuple of (x, y)
        Center coordinates in pixels
        
    Examples
    --------
    >>> # Standard center
    >>> center = set_screen_center((1920, 1080))
    >>> # center = (960, 540)
    
    >>> # Center with offset (e.g., for optical calibration)
    >>> center = set_screen_center((1920, 1080), center_offset_pix=(10, -5))
    >>> # center = (970, 535)
    """
    width, height = size_pix
    center_x = width // 2 + center_offset_pix[0]
    center_y = height // 2 + center_offset_pix[1]
    
    return (center_x, center_y)


def save_gamma_table(
    monitor_name: str,
    filepath: Union[str, Path],
    format: str = "npy"
) -> None:
    """
    Save gamma table to file for backup or transfer.
    
    Parameters
    ----------
    monitor_name : str
        Name of the monitor configuration
    filepath : str or Path
        Path where to save the gamma table
    format : str, optional
        File format: 'npy' (numpy) or 'txt' (text) (default: 'npy')
        
    Examples
    --------
    >>> save_gamma_table("left_monitor", "gamma_tables/left_gamma.npy")
    """
    mon = monitors.Monitor(monitor_name)
    gamma_grid = mon.getGammaGrid()
    
    if gamma_grid is None:
        # Convert single gamma to grid format
        gamma = mon.getGamma()
        if gamma is not None:
            if isinstance(gamma, (int, float)):
                # Create linear lookup table for single gamma
                levels = np.linspace(0, 1, 256) ** (1.0 / gamma)
                gamma_grid = [levels, levels, levels]
            else:
                # Create lookup tables for each channel
                gamma_grid = [
                    np.linspace(0, 1, 256) ** (1.0 / gamma[0]),
                    np.linspace(0, 1, 256) ** (1.0 / gamma[1]),
                    np.linspace(0, 1, 256) ** (1.0 / gamma[2])
                ]
        else:
            raise ValueError(f"No gamma calibration found for monitor '{monitor_name}'")
    
    filepath = Path(filepath)
    
    if format == "npy":
        np.save(filepath, np.array(gamma_grid))
    elif format == "txt":
        np.savetxt(filepath, np.array(gamma_grid).T, fmt='%.6f', delimiter='\t')
    else:
        raise ValueError(f"Unsupported format: {format}. Use 'npy' or 'txt'.")


def load_gamma_table_from_file(
    monitor_name: str,
    filepath: Union[str, Path],
    format: str = "npy"
) -> monitors.Monitor:
    """
    Load gamma table from file and apply to monitor configuration.
    
    Parameters
    ----------
    monitor_name : str
        Name of the monitor configuration to update
    filepath : str or Path
        Path to the gamma table file
    format : str, optional
        File format: 'npy' (numpy) or 'txt' (text) (default: 'npy')
        
    Returns
    -------
    monitors.Monitor
        The updated Monitor object
        
    Examples
    --------
    >>> mon = load_gamma_table_from_file("left_monitor", "gamma_tables/left_gamma.npy")
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"Gamma table file not found: {filepath}")
    
    if format == "npy":
        gamma_grid = np.load(filepath)
    elif format == "txt":
        gamma_grid = np.loadtxt(filepath).T
    else:
        raise ValueError(f"Unsupported format: {format}. Use 'npy' or 'txt'.")
    
    # Ensure shape is (3, 256) for RGB channels
    if gamma_grid.shape[0] == 256 and gamma_grid.shape[1] == 3:
        gamma_grid = gamma_grid.T
    
    if gamma_grid.shape != (3, 256):
        raise ValueError(f"Gamma table must have shape (3, 256) for RGB channels, "
                        f"got {gamma_grid.shape}")
    
    mon = monitors.Monitor(monitor_name)
    mon.setGammaGrid([gamma_grid[0], gamma_grid[1], gamma_grid[2]])
    mon.save()
    
    return mon


def get_monitor_calibration_info(monitor_name: str) -> Dict:
    """
    Get all calibration information for a monitor.
    
    Parameters
    ----------
    monitor_name : str
        Name of the monitor configuration
        
    Returns
    -------
    dict
        Dictionary containing all monitor calibration information
        
    Examples
    --------
    >>> info = get_monitor_calibration_info("left_monitor")
    >>> print(info['gamma'], info['size_pix'])
    """
    mon = monitors.Monitor(monitor_name)
    
    center = set_screen_center(mon.getSizePix())
    
    return {
        'name': monitor_name,
        'width_cm': mon.getWidth(),
        'distance_cm': mon.getDistance(),
        'size_pix': mon.getSizePix(),
        'gamma': mon.getGamma(),
        'gamma_grid': mon.getGammaGrid(),
        'center_pix': center,
    }