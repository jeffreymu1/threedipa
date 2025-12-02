# vizlab3d

A Python package for creating 3D vision psychology experiments using PsychoPy and haploscope displays.

## Installation

### From Source

1. Clone or download this repository
2. Navigate to the repository directory
3. Install the package:

```bash
pip install -e .
```

Or for a regular installation:

```bash
pip install .
```

### Requirements

- Python >= 3.10
- See `requirements.txt` or `pyproject.toml` for full dependency list

## Quick Start

```python
import threedipa
from threedipa.renderer import HaplscopeRender2D, monitor_settings, physical_calibration
from threedipa.stimuli import Stimulus2DImage
from threedipa.procedure import OneIntervalDraw
import threedipa.utils as utils

# Create renderer
renderer = HaplscopeRender2D(physical_calibration, monitor_settings, debug_mode=True)

# Load stimulus
stimulus = Stimulus2DImage(
    left_image_path="path/to/left.png",
    right_image_path="path/to/right.png"
)

# Use in your experiment
# ...
```

## Package Structure

- `threedipa.renderer` - Haploscope rendering classes and utilities
- `threedipa.stimuli` - Stimulus classes for 2D stereoscopic images
- `threedipa.utils` - Utility functions and phase tracking
- `threedipa.procedure` - Experiment procedure functions
- `threedipa.monitor_calibration` - Monitor calibration utilities

## Documentation

See the `templates/` directory for example experiments.

## License

See LICENSE file for details.

