"""Simple render test for haploscope using PsychoPy, Stimulus2D, and HaplscopeRender2D."""
from __future__ import annotations

import numpy as np
from psychopy import core
from psychopy.hardware import keyboard

from threedipa.renderer.haploscopeRender import HaplscopeRender2D
from threedipa.renderer.haploscopeConfig import monitor_settings, physical_calibration
from threedipa.stimuli.stimulus2D import Stimulus2DImage


def main():
    # Create simple test images as numpy arrays
    # Left image: red square
    left_image_array = np.zeros((200, 200, 3), dtype=np.uint8)
    left_image_array[:, :, 0] = 255  # Red channel
    
    # Right image: blue square
    right_image_array = np.zeros((200, 200, 3), dtype=np.uint8)
    right_image_array[:, :, 2] = 255  # Blue channel
    
    # Create stimulus object with paths set to None
    stimulus = Stimulus2DImage(
        left_image_path=None,
        right_image_path=None,
        visual_size_degrees=(5.0, 5.0)  # 5 degrees visual angle
    )
    
    # Set numpy arrays directly using set_images
    stimulus.set_images(
        left_image=left_image_array,
        right_image=right_image_array
    )

    # Create renderer
    fixation_distance = 50  # cm
    iod = 64  # mm
    renderer = HaplscopeRender2D(
        fixation_distance=fixation_distance,
        iod=iod,
        physical_calibration=physical_calibration,
        screen_config=monitor_settings,
        debug_mode=True,  # Use debug mode for testing
    )
    
    # Render for a few seconds
    clock = core.Clock()
    clock.reset()
    kb = keyboard.Keyboard()
    
    print("Rendering stimulus for 3 seconds...")
    print("Press ESC to exit early")
    
    while clock.getTime() < 10.0:
        renderer.draw_image_stimulus(stimulus)
        renderer.render_screen()
        
        # Check for escape key
        keys = kb.getKeys(['escape'], waitRelease=False)
        if keys:
            break
    
    # Close windows
    renderer.close_windows()
    print("Test complete!")


if __name__ == "__main__":
    main()
