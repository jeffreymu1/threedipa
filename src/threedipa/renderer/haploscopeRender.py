# vizlab3D libraries
from threedipa import utils
from abc import ABC, abstractmethod
from . import utils as renderer_utils
from psychopy import visual
from threedipa.stimuli.stimuli import make_fixation_cross


class HaplscopeRender(ABC):
    """Abstract base class for haploscope renders."""
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

class HaplscopeRender2D(HaplscopeRender):
    """Render the stimulus on the haploscope."""

    def __init__(
        self,
        fixation_distance,
        iod,
        physical_calibration,
        screen_config,
        debug_mode,
        fixation_cross_degrees: float = 0.25,
    ):
        self.fixation_distance = fixation_distance
        self.iod = iod
        self.physical_calibration = physical_calibration
        self.config = screen_config
        self.debug_mode = debug_mode
        self.fixation_cross_pixels = fixation_cross_degrees
        self.windows = renderer_utils.setup_haploscope_windows(
            size_pix=self.config["size_pix"],
            fullscr=self.config["full_screen"],
        ) if not self.debug_mode else renderer_utils.setup_haploscope_windows(
            size_pix=[800,600],
            fullscr=False,
        )
        self.pixel_by_cm = self.config["size_pix"][0] / self.config["size_cm"][0]

        self.pixel_per_degree = utils.pixels_by_visual_degree(
            self.config["size_cm"][0],
            self.fixation_distance,
            self.pixel_by_cm
        )

    def draw_physical_calibration(self):
        # Draw the physical calibration on the windows.
        calibration_text = renderer_utils.calc_physical_calibration(
            iod=self.iod,
            focal_distance=self.fixation_distance,
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
            size_degrees = (self.fixation_cross_pixels, self.fixation_cross_pixels)
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
    ) -> tuple[visual.ImageStim, visual.ImageStim]:
        """Draw the image stimulus on the windows."""

        stim_left = visual.ImageStim(
            self.windows[0],
            image=str(stimulus.left_image),
            units=self.windows[0].units,
            **kwargs
        ).draw()
        stim_right = visual.ImageStim(
            self.windows[1],
            image=str(stimulus.right_image),
            units=self.windows[1].units,
            **kwargs
        ).draw()
        
    def render_screen(
        self
    ):
        self.windows[0].flip()
        self.windows[1].flip()

    def close_windows(self):
        """Close the windows."""
        self.windows[0].close()
        self.windows[1].close()

class SingleScreenRender2D(HaplscopeRender):
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
        ) if not self.debug_mode else haplscope_utils.setup_single_window(
            size_pix=[800,600],
            fullscr=False,
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


class HaplscopeRender3D(HaplscopeRender):
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