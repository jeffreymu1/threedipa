# Installation Guide for vizlab3d

This guide explains how to set up and install the vizlab3d package on a new computer.

## Prerequisites

- Python 3.10 or higher
- pip (Python package installer)
- Git (if installing from repository)

## Installation Steps

### Option 1: Install from Local Source (Development)

1. **Copy the entire project folder** to the new computer

2. **Open a terminal/command prompt** in the project directory

3. **Create a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   ```

4. **Activate the virtual environment**:
   - Windows: `.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`

5. **Install the package**:
   ```bash
   pip install -e .
   ```
   
   The `-e` flag installs in "editable" mode, so changes to the source code are immediately available.

### Option 2: Install as Regular Package

Follow steps 1-4 above, then:
```bash
pip install .
```

### Option 3: Install from Requirements Only

If you only want to install dependencies without the package itself:
```bash
pip install -r requirements.txt
```

## Verify Installation

Test that the package is installed correctly:

```python
python -c "import threedipa; print(threedipa.__version__)"
```

You should see: `0.0.1`

## Running Example Experiments

Example experiments are in the `templates/` directory. To run the Johnston template:

```bash
cd templates/johnstonTemplate
python johnstonTemplate.py
```

## Troubleshooting

### Import Errors

If you get import errors, make sure:
1. The package is installed: `pip list | grep vizlab3d`
2. You're using the correct Python environment
3. All dependencies are installed: `pip install -r requirements.txt`

### PsychoPy Issues

PsychoPy may require additional system dependencies:
- **Windows**: Usually works out of the box
- **macOS**: May need Xcode command line tools
- **Linux**: May need additional graphics libraries

### Missing Dependencies

If you encounter missing module errors, install all dependencies:
```bash
pip install -r requirements.txt
```

## Package Structure

After installation, the package will be available as:
- `threedipa` - Main package
- `threedipa.renderer` - Rendering classes
- `threedipa.stimuli` - Stimulus classes
- `threedipa.utils` - Utility functions

## Next Steps

1. Review the example in `templates/johnstonTemplate/`
2. Check the README.md for usage examples
3. Explore the package documentation

