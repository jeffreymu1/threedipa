"""Simple render test for haploscope using PsychoPy, Stimulus2D, and HaplscopeRender2D."""
from __future__ import annotations

import numpy as np
from psychopy import core
import psychopy.visual as visual


from vizlab3d.renderer.haploscopeRender2D import HaplscopeRender2D
from vizlab3d.stimulus.stimulus2D import StimulusImage


def main():
    config = {}
    config["screen_size"] = (1280, 720)
    config["full_screen"] = False
    
    # Create simple test images as numpy arrays
    # Left image: red square
    left_stimulus = np.zeros((200, 200, 3), dtype=np.uint8)
    left_stimulus[:, :, 0] = 255  # Red channel
    left_image =visual.ImageStim(
        win=left_window,
        image=left_stimulus,
        pos=(0, 0),
        size=(200, 200)
    )
    
    # Right image: blue square
    right_image = np.zeros((200, 200, 3), dtype=np.uint8)
    right_image[:, :, 2] = 255  # Blue channel
    



    # Create renderer
    renderer = HaplscopeRender2D(
        screen_config=config,
    )
    
    # Render for a few seconds
    clock = core.Clock()
    clock.reset()
    
    print("Rendering stimulus for 3 seconds...")
    print("Press ESC to exit early")
    
    while clock.getTime() < 3.0:
        renderer.render_stimulus(stimulus)
    
    # Close windows
    renderer.close_windows()
    print("Test complete!")


if __name__ == "__main__":
    main()

