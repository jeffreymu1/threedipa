from threedipa import utils
from abc import ABC, abstractmethod
from . import utils as renderer_utils
from psychopy import visual
from threedipa.stimuli.stimuli import make_fixation_cross
import numpy as np


class ExperimentRenderer(ABC):
    """Abstract base class for renders."""
    @abstractmethod
    def draw_physical_calibration(self):
        pass

    @abstractmethod
    def draw_fixation_cross(self):
        pass

    @abstractmethod
    def draw_image_stimulus(self):
        pass

    @abstractmethod
    def render_screen(self):
        pass

    @abstractmethod
    def close_windows(self):
        pass

class HaplscopeRender2D(ExperimentRenderer):
    """Render the stimulus on the haploscope."""

    def __init__(
        self,
        fixation_distance,
        iod,
        physical_calibration,
        screen_config,
        debug_mode: bool = False,
        fixation_cross_degrees: float = 0.5,
    ):
        self.fixation_distance = fixation_distance
        self.iod = iod
        self.physical_calibration = physical_calibration
        self.config = screen_config
        self.debug_mode = debug_mode
        self.fixation_cross_degrees = fixation_cross_degrees
        self.windows = renderer_utils.setup_haploscope_windows(
            size_pix=self.config["size_pix"],
            fullscr=self.config["full_screen"],
        ) if not self.debug_mode else renderer_utils.setup_haploscope_windows(
            size_pix=[800,600],
            fullscr=False,
        )
        self.pixel_by_cm_density = self.config["size_pix"][0] / self.config["size_cm"][0]

        self.pixel_per_degree = utils.pixels_by_visual_degree(
            self.config["size_cm"][0],
            self.fixation_distance,
            self.pixel_by_cm_density
        )

    def draw_physical_calibration(self):
        # Draw the physical calibration on the windows in mm.
        calibration_text = renderer_utils.calc_physical_calibration(
            iod=self.iod,
            focal_distance_mm=self.fixation_distance * 10,  # convert cm to mm
            config=self.physical_calibration
        )
        # Convert dictionary to string
        calibration_text = "\n".join(
            [f"{key}: {value}mm" for key, value in calibration_text.items()]
            )
        calibration_text = calibration_text + "\nPress Enter to continue"
        visual.TextStim(
            self.windows[0],
            text=calibration_text,
            units=self.windows[0].units,
            pos=(0, 0),
            color='white'
        ).draw()
        visual.TextStim(
            self.windows[1],
            text=calibration_text,
            units=self.windows[1].units,
            pos=(0, 0),
            color='white'
        ).draw()

    def draw_text(self, text: str, pos: tuple[float, float] = (0, 0)):
        visual.TextStim(
            self.windows[0],
            text=text,
            units=self.windows[0].units,
            pos=pos,
            color='white'
        ).draw()
        visual.TextStim(
            self.windows[1],
            text=text,
            units=self.windows[1].units,
            pos=pos,
            color='white'
        ).draw()

    def draw_fixation_cross(
        self,
        size_degrees: tuple[float, float] = [],
        color: str = 'white',
        pos : tuple[float, float] = (0, 0)
    ):
        """Draw the fixation cross on the windows."""
        if size_degrees == []:
            size_degrees = (self.fixation_cross_degrees, self.fixation_cross_degrees)
        horizontal_in_pixels = size_degrees[0] * self.pixel_per_degree
        vertical_in_pixels = size_degrees[1] * self.pixel_per_degree

        size_pixels = (horizontal_in_pixels, vertical_in_pixels)
        l_fixation, r_fixation = make_fixation_cross(
            self.windows, size_pixels, color, pos)
        # l_fixation and r_fixation are tuples of (vertical, horizontal) lines
        # Draw left fixation cross
        l_fixation[0].draw()  # vertical line
        l_fixation[1].draw()  # horizontal line
        # Draw right fixation cross
        r_fixation[0].draw()  # vertical line
        r_fixation[1].draw()  # horizontal line

    def draw_image_stimulus(
        self, stimulus, kwargs: dict = {}
    ):
        """Draw the image stimulus on the windows.
        
        Supports both numpy arrays and file paths for images.
        """
        if stimulus.visual_size_degrees is None:
            raise ValueError("Visual size in degrees must be set for the stimulus.")
        stimulus_size_pixels = (
            stimulus.visual_size_degrees[0] * self.pixel_per_degree,
            stimulus.visual_size_degrees[1] * self.pixel_per_degree
        )
        
        # Handle numpy arrays vs file paths
        # If it's a numpy array, pass it directly; otherwise convert to string for file path
        left_image = stimulus.left_image if isinstance(stimulus.left_image, np.ndarray) else str(stimulus.left_image)
        right_image = stimulus.right_image if isinstance(stimulus.right_image, np.ndarray) else str(stimulus.right_image)
        
        stim_left = visual.ImageStim(
            self.windows[0],
            image=left_image,
            units="pix",
            size=stimulus_size_pixels,
            **kwargs
        ).draw()
        stim_right = visual.ImageStim(
            self.windows[1],
            image=right_image,
            units="pix",
            size=stimulus_size_pixels,
            **kwargs
        ).draw()
    
    def convert_visual_angle_to_pixels(self, angle):
        """ Convert visual angle in degrees to pixels on the screen """
        return self.pixel_per_degree * angle
    
    def convert_centimeters_to_pixels(self, size_cm):
        """ Convert physical size to pixels on the screen """
        size_degrees = utils.degree_from_width_cm(size_cm, self.fixation_distance)
        return self.convert_visual_angle_to_pixels(size_degrees)

    
    def draw_probe(
        self, probe_stimulus
    ):
        """Draw the probe stimulus on the windows."""
        # Update the amount of pixel movement.
        magnitude = probe_stimulus.getMagnitude()
        if probe_stimulus.units == "centimeters":
            magnitude_pixels = self.convert_centimeters_to_pixels(magnitude)
            probe_stimulus.setMagnitudePixels(magnitude_pixels)
        elif probe_stimulus.units == "degrees":
            magnitude_pixels = self.convert_visual_angle_to_pixels(magnitude)
            probe_stimulus.setMagnitudePixels(magnitude_pixels)
        elif probe_stimulus.units == "pixels":
            magnitude_pixels = magnitude
            probe_stimulus.setMagnitudePixels(magnitude_pixels)
        probe_stimulus.draw(self.windows[0])
        probe_stimulus.draw(self.windows[1])

    def render_screen(
        self
    ):
        self.windows[0].flip()
        self.windows[1].flip()

    def close_windows(self):
        """Close the windows."""
        self.windows[0].close()
        self.windows[1].close()

class SingleScreenRender2D(ExperimentRenderer):
    """Render the stimulus on the haploscope."""

    def __init__(
        self,
        physical_calibration,
        screen_config,
        debug_mode,
    ):
        self.physical_calibration = physical_calibration
        self.config = screen_config
        self.debug_mode = debug_mode
        self.window = renderer_utils.setup_single_window(
            size_pix=self.config["size_pix"],
            fullscr=self.config["full_screen"],
            stereo=False,
        ) if not self.debug_mode else renderer_utils.setup_single_window(
            size_pix=[800,600],
            fullscr=False,
            stereo=False,
        )

    def draw_fixation_cross(
        self,
        size: tuple[float, float] = (1.0, 1.0),
        color: str = 'white',
        pos : tuple[float, float] = (0, 0)
    ):
        """Draw the fixation cross on the windows."""
        l_fixation, _ = make_fixation_cross(
            self.window, size, color, pos)
        l_fixation[0].draw()  # vertical line
        l_fixation[1].draw()  # horizontal line

    def draw_image_stimulus(
        self, stimulus, kwargs: dict = {}
    ) -> tuple[visual.ImageStim, visual.ImageStim]:
        """Draw the image stimulus on the windows."""

        visual.ImageStim(
            self.window,
            image=str(stimulus.left_image),
            units=self.window.units,
            **kwargs
        ).draw()
        
    def render_screen(
        self
    ):
        self.window.flip()

    def close_windows(self):
        """Close the windows."""
        self.window.close()


class HaplscopeRender3D(ExperimentRenderer):
    """Render the stimulus on the haploscope."""

    def __init__(
        self,
        screen_config,
    ):
        self.config = screen_config
        self.windows = renderer_utils.setup_haploscope_windows(
            size_pix=self.config["screen_size"],
            fullscr=self.config["full_screen"],
        )


class ShutterRenderer3D(ExperimentRenderer):
    """Render the stimulus using quad buffer stereo with shutter glasses.
    
    This class uses a single window with quad buffer stereo mode to render
    separate images to the left and right eye using shutter glasses synchronization.
    """

    def __init__(
        self,
        fixation_distance,
        iod,
        physical_calibration,
        screen_config,
        debug_mode: bool = False,
        fixation_cross_degrees: float = 0.5,
    ):
        self.fixation_distance = fixation_distance
        self.iod = iod
        self.physical_calibration = physical_calibration
        self.config = screen_config
        self.debug_mode = debug_mode
        self.fixation_cross_degrees = fixation_cross_degrees
        
        # Create a single window with quad buffer stereo mode for shutter glasses
        size_pix = self.config["size_pix"] if not self.debug_mode else [800, 600]
        fullscr = self.config["full_screen"] if not self.debug_mode else False
        
        self.window = renderer_utils.setup_single_window(
            size_pix=size_pix,
            fullscr=fullscr,
            monitor_number=0,
            units="pix",
            color=(-1, -1, -1),  # Black background (PsychoPy uses -1 to 1 range)
            waitBlanking=True,
            stereo=True,  # Enable stereo rendering by using quad buffer for shutter glasses
        )
        
        self.pixel_by_cm_density = self.config["size_pix"][0] / self.config["size_cm"][0]

        self.pixel_per_degree = utils.pixels_by_visual_degree(
            self.config["size_cm"][0],
            self.fixation_distance,
            self.pixel_by_cm_density
        )

    def draw_physical_calibration(self):
        """Draw the physical calibration on the window in mm."""
        calibration_text = "Ensure monitor is moved to the correct position.\n Press Enter to continue"
        
        # Draw to both eyes
        for eye in ['left', 'right']:
            self.window.setBuffer(eye)
            visual.TextStim(
                self.window,
                text=calibration_text,
                units=self.window.units,
                pos=(0, 0),
                color='white'
            ).draw()

    def draw_text(self, text: str, pos: tuple[float, float] = (0, 0)):
        """Draw text to both eyes."""
        for eye in ['left', 'right']:
            self.window.setBuffer(eye)
            visual.TextStim(
                self.window,
                text=text,
                units=self.window.units,
                pos=pos,
                color='white'
            ).draw()

    def draw_fixation_cross(
        self,
        size_degrees: tuple[float, float] = [],
        color: str = 'white',
        pos : tuple[float, float] = (0, 0)
    ):
        """Draw the fixation cross on both eyes."""
        if size_degrees == []:
            size_degrees = (self.fixation_cross_degrees, self.fixation_cross_degrees)
        horizontal_in_pixels = size_degrees[0] * self.pixel_per_degree
        vertical_in_pixels = size_degrees[1] * self.pixel_per_degree

        size_pixels = (horizontal_in_pixels, vertical_in_pixels)
        
        # Draw to both eyes
        for eye in ['left', 'right']:
            self.window.setBuffer(eye)
            # Create vertical line
            vertical = visual.Line(
                win=self.window,
                start=(0, -size_pixels[1]/2),
                end=(0, size_pixels[1]/2),
                units="pix",
                pos=pos,
                color=color
            )
            # Create horizontal line
            horizontal = visual.Line(
                win=self.window,
                start=(-size_pixels[0]/2, 0),
                end=(size_pixels[0]/2, 0),
                units="pix",
                pos=pos,
                color=color
            )
            # Draw fixation cross
            vertical.draw()
            horizontal.draw()

    def draw_image_stimulus(
        self, stimulus, kwargs: dict = {}
    ):
        """Draw the image stimulus to left and right eyes.
        
        Supports both numpy arrays and file paths for images.
        """
        if stimulus.visual_size_degrees is None:
            raise ValueError("Visual size in degrees must be set for the stimulus.")
        stimulus_size_pixels = (
            stimulus.visual_size_degrees[0] * self.pixel_per_degree,
            stimulus.visual_size_degrees[1] * self.pixel_per_degree
        )
        
        # Handle numpy arrays vs file paths
        # If it's a numpy array, pass it directly; otherwise convert to string for file path
        left_image = stimulus.left_image if isinstance(stimulus.left_image, np.ndarray) else str(stimulus.left_image)
        right_image = stimulus.right_image if isinstance(stimulus.right_image, np.ndarray) else str(stimulus.right_image)
        
        # Draw left image to left eye buffer
        self.window.setBuffer('left')
        visual.ImageStim(
            self.window,
            image=left_image,
            units="pix",
            size=stimulus_size_pixels,
            **kwargs
        ).draw()
        
        # Draw right image to right eye buffer
        self.window.setBuffer('right')
        visual.ImageStim(
            self.window,
            image=right_image,
            units="pix",
            size=stimulus_size_pixels,
            **kwargs
        ).draw()
    
    def convert_visual_angle_to_pixels(self, angle):
        """Convert visual angle in degrees to pixels on the screen."""
        return self.pixel_per_degree * angle
    
    def convert_centimeters_to_pixels(self, size_cm):
        """Convert physical size to pixels on the screen."""
        size_degrees = utils.degree_from_width_cm(size_cm, self.fixation_distance)
        return self.convert_visual_angle_to_pixels(size_degrees)

    def draw_probe(
        self, probe_stimulus
    ):
        """Draw the probe stimulus to both eyes."""
        # Update the amount of pixel movement.
        magnitude = probe_stimulus.getMagnitude()
        if probe_stimulus.units == "centimeters":
            magnitude_pixels = self.convert_centimeters_to_pixels(magnitude)
            probe_stimulus.setMagnitudePixels(magnitude_pixels)
        elif probe_stimulus.units == "degrees":
            magnitude_pixels = self.convert_visual_angle_to_pixels(magnitude)
            probe_stimulus.setMagnitudePixels(magnitude_pixels)
        elif probe_stimulus.units == "pixels":
            magnitude_pixels = magnitude
            probe_stimulus.setMagnitudePixels(magnitude_pixels)
        
        # Draw to both eyes
        for eye in ['left', 'right']:
            self.window.setBuffer(eye)
            probe_stimulus.draw(self.window)

    def render_screen(
        self
    ):
        """Render the screen - flip() handles shutter synchronization automatically."""
        self.window.flip()

    def close_windows(self):
        """Close the window."""
        self.window.close()


