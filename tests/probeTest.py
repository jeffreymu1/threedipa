"""Simple test for ShapeOutlineProbe with semiellipse function.

Renders a semiellipse probe where magnitude controls the ellipse stretch/compression.
Adjust magnitude using numpad 3 (decrease) and 6 (increase).
Press ESC to exit.
"""
from __future__ import annotations

import sys
import pathlib
import numpy as np
from psychopy import core, visual
from psychopy.hardware import keyboard

# Add src to path so local package 'threedipa' can be imported
repo_root = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root / 'src'))

from threedipa.stimuli.probe2D import ShapeOutlineProbe


def parabolaProbe(x: float, magnitude: float) -> float:
    """
    Function that controls the stretch/compression of parabola probe.
    """
    radius = 50 # in pixels, change with probe length
    y = (2*np.sqrt(x**2) / radius)**2 * magnitude
    return y


def main():
    # Window configuration
    config = {
        "size_pix": (1280, 720),
        "size_cm": (35, 20),
        "full_screen": False,
    }
    
    # Create PsychoPy window
    win = visual.Window(
        size=config["size_pix"],
        fullscr=config["full_screen"],
        units='pix',
        color=(-1, -1, -1),  # Black background
    )
    
    # Initialize magnitude
    magnitude = 20
    magnitude_step = 5
    
    # Create probe with parabolaProbe function
    probe = ShapeOutlineProbe(
        probe_func=parabolaProbe,
        magnitude=magnitude,
        win=win,
        x_range=(-50, 50),
        segments=100,
        line_width_pix=3,
        rotate_90=True,
        color='white'
    )
    
    # Create text to display current magnitude
    magnitude_text = visual.TextStim(
        win=win,
        text=f"Magnitude: {magnitude}",
        pos=(0, -300),
        height=20,
        color='white'
    )
    
    # Instructions text
    instructions = visual.TextStim(
        win=win,
        text="Numpad 3: Decrease  |  Numpad 6: Increase  |  ESC: Exit",
        pos=(0, 300),
        height=16,
        color=(0.5, 0.5, 0.5),
        wrapWidth=1200
    )
    
    # Keyboard handler
    kb = keyboard.Keyboard()
    
    # Main rendering loop
    clock = core.Clock()
    running = True
    
    print("Starting probe test...")
    print("Use numpad 3 to decrease magnitude, numpad 6 to increase")
    print("Press ESC to exit")
    
    while running:
        # Check for key presses
        keys = kb.getKeys(['a', 's', 'escape'], waitRelease=False)
        
        for key in keys:
            if key.name == 'escape':
                running = False
            elif key.name == 'a':
                magnitude = max(0, magnitude - magnitude_step)
                probe.setMagnitude(magnitude)
                probe.setMagnitudePixels(magnitude)
                print(f"Magnitude: {magnitude}")
            elif key.name == 's':
                magnitude += magnitude_step
                probe.setMagnitude(magnitude)
                probe.setMagnitudePixels(magnitude)
                print(f"Magnitude: {magnitude}")
        
        # Update magnitude text
        magnitude_text.text = f"Magnitude: {magnitude}"
        
        # Draw stimuli
        probe.draw(win=win)
        magnitude_text.draw()
        instructions.draw()
        
        # Flip the window
        win.flip()
    
    # Clean up
    win.close()
    core.quit()
    print("Test complete!")


if __name__ == "__main__":
    main()
