import os

# Third-party libraries
from psychopy import core, gui
from psychopy.data import ExperimentHandler, TrialHandler
from psychopy.hardware import keyboard

# Class built functions
import threedipa.utils as utils
from threedipa.renderer.haploscopeRender import HaplscopeRender2D
from threedipa.renderer.haploscopeConfig import monitor_settings, physical_calibration
from threedipa.procedure import OneIntervalDraw
from threedipa.stimuli.stimulus2D import Stimulus2DImage

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
        # For the second part of presentation, show the stimulus
        elif trial_time.getTime() <= config['StimulusDuration'] + config['FixationDuration']:
            phaseTracker.set_stimulus_phase(utils.StimulusPhase.STIMULUS)
        # Do not draw any stimulus and wait for a response
        elif trial_time.getTime() > config['StimulusDuration'] + config['FixationDuration']:
            phaseTracker.set_stimulus_phase(utils.StimulusPhase.NONE)
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
    exp_dir = './templates/johnstonTemplate/'
    data_file_name = exp_dir + f"data/johnston_{info['Participant ID']}_{info['Session']}"
    parameters = utils.parse_parameters_file(exp_dir + 'parameters.txt')
    debug_mode = parameters['parameters']['Debug']

    # Create data directory if it doesn't exist
    data_dir = exp_dir + '/data'
    os.makedirs(data_dir, exist_ok=True)

    # 3. Create trial list (all combinations of factors)
    trialList = utils.createFactorialTrialList(parameters['factors'])
    repetitions = parameters['parameters']['Repetitions']
    fixationDistance = parameters['parameters']['FixationDistance']
    stimulusVisualAngle = parameters['parameters']['VisualAngle']
    
    # 4. Create ExperimentHandler and TrialHandler
    thisExp = ExperimentHandler(
        name='johnston_stereopsis',
        version='1.0',
        extraInfo=info,
        runtimeInfo=None,
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
    kb = keyboard.Keyboard(clock=core.Clock())
    # initialize recording variables
    trial_time = core.Clock()
    rt = 0.0
    response_key = None

    # 7. Calibrate the physical haploscope
    renderer.draw_physical_calibration()
    renderer.render_screen()
    kb.waitKeys(keyList=['return', ], waitRelease=True)
    
    # 8. Give instructions to the participant
    instructions_text = ("Press 3 if the stimulus is stretched and 6 if it is squashed."
    + "\nPress enter to begin the experiment.")
    renderer.draw_text(instructions_text, pos=(0, 0))
    renderer.render_screen()
    kb.waitKeys(keyList=['return'], waitRelease=True)
    
    # 9. Experiment loop to run each trial
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
            OneIntervalDraw(renderer, stimulus, phaseTracker.get_stimulus_phase())

            if phaseTracker.get_response_phase() == utils.ResponsePhase.WAIT_FOR_RESPONSE:
                kb.clock.reset()
                kb.clearEvents()
                response_key = kb.waitKeys(keyList=['num_3', '3', '6', 'num_6', 'escape'], waitRelease=False)
                
                if response_key:
                    rt = kb.clock.getTime()
                    phaseTracker.set_response_phase(utils.ResponsePhase.RESPONSE_RECEIVED)
                    break

        if response_key[0].name == 'escape':
            # Exit the experiment
            exit_experiment(phaseTracker)
            break
        else:
            phaseTracker.set_experiment_phase(utils.ExperimentPhase.POST_TRIAL)
        

        # Remove 'num_' prefix from key name if input is from numpad
        response_name = response_key[0].name
        if response_name.startswith('num_'):
            response_name = response_name[4:]  # Remove first 4 characters ('num_')


        # Store data and end the entry line
        trials.addData('stimulus_id', getattr(stimulus, 'stimulus_id', ''))
        trials.addData('response_key', response_name)
        trials.addData('rt_s', rt)
        
        # Move to the next line of the experimentHandler data management
        thisExp.nextEntry()

    # 8. Save and close
    thisExp.saveAsWideText(data_file_name + '.csv')
    renderer.close_windows()
    core.quit()
        
if __name__ == "__main__":
    main()
