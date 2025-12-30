# Third-party libraries
from psychopy import core, gui
from psychopy.data import ExperimentHandler, TrialHandler
from psychopy.hardware import keyboard
import numpy as np

# Class built functions
import threedipa.utils as utils
from threedipa.renderer.haploscopeRender import HaplscopeRender2D
from threedipa.renderer.haploscopeConfig import monitor_settings, physical_calibration
from threedipa.procedure import stimulusAdjustmentDraw
from threedipa.stimuli.stimulus2D import Stimulus2DImage
from threedipa.stimuli.probe2D import ShapeOutlineProbe

# Exit protocols
def exit_experiment(phaseTracker):
    # Draw a blank screen
    phaseTracker.set_stimulus_phase(utils.StimulusPhase.NONE)
    # End the experiment
    phaseTracker.set_experiment_phase(utils.ExperimentPhase.END)


# Controls the timing of the trial
def trialPhase_timing(phaseTracker: utils.PhaseTracker, trial_time, config):
    # Only run when in the trial phase
    if phaseTracker.get_experiment_phase() == utils.ExperimentPhase.TRIAL:
        # For the first part of presentation, show the fixation cross
        if trial_time.getTime() <= config['FixationDuration']:
            phaseTracker.set_stimulus_phase(utils.StimulusPhase.FIXATION)
        # For the second part of presentation, show the stimulus and probe
        elif trial_time.getTime() > config['FixationDuration']:
            phaseTracker.set_stimulus_phase(utils.StimulusPhase.STIMULUS)
            phaseTracker.set_response_phase(utils.ResponsePhase.WAIT_FOR_RESPONSE)
            

def load_stimulus(
    stimulusDepth: float, 
    stimulusHeight: float, 
    exp_dir: str
) -> Stimulus2DImage:
    # Load the stimulus from the stimulus library
    stimulus = Stimulus2DImage(
        left_image_path=exp_dir+'stimuli/10_L.png',
        right_image_path=exp_dir+'stimuli/10_R.png'
    )
    return stimulus

def reset_phase_tracker(phaseTracker: utils.PhaseTracker):
    phaseTracker.set_experiment_phase(utils.ExperimentPhase.PRE_TRIAL)
    phaseTracker.set_stimulus_phase(utils.StimulusPhase.FIXATION)
    phaseTracker.set_response_phase(utils.ResponsePhase.NO_RESPONSE)

def main():
    # 1. Collect participant info
    info = {'Participant ID': 'test', 'IOD': '64', 'Session': '1'}
    dlg = gui.DlgFromDict(info, title='Johnston Stereopsis')

    # 2. Load parameters
    exp_dir = './templates/probeTemplate/'
    data_file_name = exp_dir + f"data/johnston_{info['Participant ID']}_{info['Session']}"
    parameters = utils.parse_parameters_file(exp_dir + 'parameters.txt')
    debug_mode = parameters['parameters']['Debug']

    # 3. Create trial list (all combinations of factors)
    trialList = utils.createFactorialTrialList(parameters['factors'])
    repetitions = parameters['parameters']['Repetitions']
    fixationDistance = parameters['parameters']['FixationDistance']
    stimulusVisualAngle = parameters['parameters']['VisualAngle']

    # Probe parameters
    probeLengthDegree = parameters['parameters']['ProbeLength']
    magnitude_step = parameters['parameters']['ProbeLength']
    probe_y_position_degrees = parameters['parameters']['ProbeYPosition']
    
    # 4. Create ExperimentHandler and TrialHandler
    thisExp = ExperimentHandler(
        name='johnston_stereopsis',
        version='1.0',
        extraInfo=info,
        runtimeInfo=None,
        dataFileName=data_file_name
    )

    trials = TrialHandler(
        trialList=trialList,
        nReps=repetitions,
        method='sequential',
        extraInfo=thisExp.extraInfo,
        originPath=-1,
        seed=None,
        name='trials'
    )
    thisExp.addLoop(trials)
    
    # 5. Create PhaseTracker
    phaseTracker = utils.PhaseTracker()
    
    # 6. Setup renderer and input devices
    renderer = HaplscopeRender2D(
        fixation_distance=fixationDistance,
        iod=float(info['IOD']),
        physical_calibration=physical_calibration,
        screen_config=monitor_settings,
        debug_mode=debug_mode,
    )

    # 7. Define probe function and probe
    # (Function is defined here to take advantage of the renderer conversion function)
    probe_length = renderer.convert_visual_angle_to_pixels(probeLengthDegree)
    probe_half_length = probe_length / 2
    def parabolaProbe(x: float, magnitude: float) -> float:
        """
        Function that controls the stretch/compression of parabola probe.
        """
        y = (2*np.sqrt(x**2) / probe_half_length)**2 * magnitude
        return y
    
    # Create probe with parabolaProbe function
    magnitude = 0 # In centimeters
    probe_y_position_pixels = renderer.convert_visual_angle_to_pixels(probe_y_position_degrees)
    probe = ShapeOutlineProbe(
        probe_func=parabolaProbe,
        magnitude=magnitude,
        x_range=(-probe_half_length, probe_half_length),
        segments=100,
        position=[0, -probe_y_position_pixels],
        line_width_pix=3,
        rotate_90=True,
        color='white'
    )
    
    kb = keyboard.Keyboard(clock=core.Clock())
    # initialize recording variables
    trial_time = core.Clock()
    rt = 0.0

    # 8. Calibrate the physical haploscope
    renderer.draw_physical_calibration()
    renderer.render_screen()
    kb.waitKeys(keyList=['return', ], waitRelease=True)
    
    # 9. Give instructions to the participant
    instructions_text = ("Press 3 if the stimulus is stretched and 6 if it is squashed."
    + "\nPress enter to begin the experiment.")
    renderer.draw_text(instructions_text, pos=(0, 0))
    renderer.render_screen()
    kb.waitKeys(keyList=['return'], waitRelease=True)
    
    # 10. Experiment loop to run each trial
    # Iterate through the TrialHandler
    for currentTrial in trials:
        # Break trial loop if the experiment should be ended
        if phaseTracker.get_experiment_phase() == utils.ExperimentPhase.END:
            break

        # Set up the current trial variables
        reset_phase_tracker(phaseTracker)

        # Get the current trial factors
        stimulusDepth = currentTrial['Depth']
        stimulusHeight = currentTrial['halfHeight']
        stimulus = load_stimulus(stimulusDepth, stimulusHeight, exp_dir)
        stimulus.visual_size_degrees = (stimulusVisualAngle, stimulusVisualAngle)
        
        phaseTracker.set_experiment_phase(utils.ExperimentPhase.TRIAL)
        trial_time.reset()
        
        # Trial loop to run each frame of the trial
        while phaseTracker.get_experiment_phase() == utils.ExperimentPhase.TRIAL:
            # Control the timing of the trial
            # This controls when the stimulus is drawn and when the response is expected
            trialPhase_timing(phaseTracker, trial_time, parameters['parameters'])
            
            # Run the draw function
            stimulusAdjustmentDraw(renderer, stimulus, probe, phaseTracker.get_stimulus_phase())

            if phaseTracker.get_response_phase() == utils.ResponsePhase.WAIT_FOR_RESPONSE:
                response_keys = kb.getKeys(['a', 's', 'escape', 'return'], waitRelease=False)
        
                if response_keys:
                    key = response_keys.pop()
                    if key.name == 'escape':
                        exit_experiment(phaseTracker)
                        break
                    elif key.name == 'a':
                        magnitude = max(0, magnitude - magnitude_step)
                        probe.setMagnitude(magnitude)
                    elif key.name == 's':
                        magnitude += magnitude_step
                        probe.setMagnitude(magnitude)
                    elif key == 'return':
                        rt = kb.clock.getTime()
                        phaseTracker.set_stimulus_phase(utils.StimulusPhase.NONE)
                        phaseTracker.set_response_phase(utils.ResponsePhase.RESPONSE_RECEIVED)
                        phaseTracker.set_experiment_phase(utils.ExperimentPhase.POST_TRIAL)
                        break
        

        # Store data and end the entry line
        trials.addData('stimulus_id', getattr(stimulus, 'stimulus_id', ''))
        trials.addData('magnitude', magnitude)
        trials.addData('rt_s', rt)
        
        # Move to the next line of the experimentHandler data management
        thisExp.nextEntry()

    # 8. Save and close
    thisExp.saveAsWideText(data_file_name + '.csv')
    renderer.close_windows()
    core.quit()
        
if __name__ == "__main__":
    main()
