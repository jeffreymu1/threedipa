# vizlab3D libraries
from abc import ABC, abstractmethod
from . import haplscope_utils
from psychopy import visual
from ..stimuli import make_fixation_cross


class HaplscopeRender(ABC):
    """Abstract base class for haploscope renders."""
    @abstractmethod
    def get_physical_calibration(self):
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
        physical_calibration,
        screen_config,
        debug_mode,
    ):
        self.physical_calibration = physical_calibration
        self.config = screen_config
        self.debug_mode = debug_mode
        self.windows = haplscope_utils.setup_haploscope_windows(
            size_pix=self.config["size_pix"],
            fullscr=self.config["full_screen"],
        ) if not self.debug_mode else haplscope_utils.setup_haploscope_windows(
            size_pix=[800,600],
            fullscr=False,
        )

    def get_physical_calibration(self):
        return haplscope_utils.calc_physical_calibration(
            self.config["focal_distance"],
            self.config["iod"],
            self.physical_calibration
        )

    def draw_fixation_cross(
        self,
        size: tuple[float, float] = (1.0, 1.0),
        color: str = 'white',
        pos : tuple[float, float] = (0, 0)
    ):
        """Draw the fixation cross on the windows."""
        l_fixation, r_fixation = make_fixation_cross(
            self.windows, size, color, pos)
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


class HaplscopeRender3D(HaplscopeRender):
    """Render the stimulus on the haploscope."""

    def __init__(
        self,
        screen_config,
    ):
        self.config = screen_config
        self.windows = haplscope_utils.setup_haploscope_windows(
            size_pix=self.config["screen_size"],
            fullscr=self.config["full_screen"],
        )