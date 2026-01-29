"""Simple test for dot probe placement task.

Renders a dot probe where users control the x position of the dot.
Adjust x position using numpad 3 (left) and 6 (right).
Press ESC to exit.

This can be used to measure features such as maximum or minimum depth positions (relative depth)

"""
from __future__ import annotations

import sys
import pathlib
from psychopy import core, visual
from psychopy.hardware import keyboard

# Add src to path so local package 'threedipa' can be imported
repo_root = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root / 'src'))

from threedipa.stimuli.probe2D import DotProbe


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
    vertical_position = 0
    vertical_position_step = 5
    
    # Create probe with parabolaProbe function

    probe = DotProbe(win=win, pos=[0, 0], size=2, color='white', num_dots=1)
    
    # Create text to display current magnitude
    magnitude_text = visual.TextStim(
        win=win,
        text=f"Vertical Position: {vertical_position}",
        pos=(0, -300),
        height=20,
        color='white'
    )
    
    # Instructions text
    instructions = visual.TextStim(
        win=win,
        text="Numpad 3: left  |  Numpad 6: right  |  ESC: Exit",
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
    print("Use numpad 3 to move dot left, numpad 6 to move dot right")
    print("Press ESC to exit")
    
    while running:
        # Check for key presses
        keys = kb.getKeys(['num_3', '3', '6', 'num_6', 'escape'], waitRelease=False, clear=False)
        
        for key in keys:
            if key.name == 'escape':
                running = False
            elif key.name == 'num_3' or key.name == '3':
                vertical_position -= vertical_position_step
                probe.setPos([vertical_position, 0])
            elif key.name == 'num_6' or key.name == '6':
                vertical_position += vertical_position_step
                probe.setPos([vertical_position, 0])
        
        # Update magnitude text
        magnitude_text.text = f"Vertical Position: {vertical_position}"
        
        # Draw stimuli
        probe.draw()
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
