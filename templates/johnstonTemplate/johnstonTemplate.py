import threading

from psychopy import data, core, event, gui, hardware
from psychopy.data import ExperimentHandler, TrialHandler
from psychopy.hardware import keyboard


import threedipa
import threedipa.utils as utils
from threedipa.renderer import monitor_settings, physical_calibration, HaplscopeRender2D
from threedipa.procedure import OneIntervalDraw
from threedipa.stimuli import Stimulus2DImage

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
    if not dlg.OK:
        core.quit()

    # 2. Load parameters
    exp_dir = './templates/johnstonTemplate/'
    data_file_name = exp_dir + f"data/johnston_{info['Participant ID']}_{info['Session']}"
    parameters = utils.parse_parameters_file(exp_dir + 'parameters.txt')
    debug_mode = parameters['parameters']['Debug']

    # 3. Create trial list (all combinations of factors)
    trialList = utils.createFactorialTrialList(parameters['factors'])
    repetitions = parameters['parameters']['Repetitions']
    
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
    renderer = HaplscopeRender2D(physical_calibration, monitor_settings, debug_mode)
    kb = keyboard.Keyboard(clock=core.Clock())
    # initialize recording variables
    trial_time = core.Clock()
    rt = 0.0
    response_key = None
    
    # 7. Trial loop to run each trial
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
        
        phaseTracker.set_experiment_phase(utils.ExperimentPhase.TRIAL)
        trial_time.reset()
        while phaseTracker.get_experiment_phase() == utils.ExperimentPhase.TRIAL:
            # Control the timing of the trial
            # This controls when the stimulus is drawn and when the response is expected
            trialPhase_timing(phaseTracker, trial_time, parameters['parameters'])
            
            # Run the draw function
            OneIntervalDraw(renderer, stimulus, phaseTracker.get_stimulus_phase())

            if phaseTracker.get_response_phase() == utils.ResponsePhase.WAIT_FOR_RESPONSE:
                kb.clock.reset()
                kb.clearEvents()
                response_key = kb.waitKeys(keyList=['3', '6', 'escape'], waitRelease=False)
                
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
        
        # Store data and end the entry line
        trials.addData('stimulus_id', getattr(stimulus, 'stimulus_id', ''))
        trials.addData('response_key', response_key[0].name)
        trials.addData('rt_s', rt)
        
        thisExp.nextEntry()

    # 8. Save and close
    thisExp.saveAsWideText(data_file_name + '.csv')
    thisExp.saveAsPickle(data_file_name)
    renderer.close_windows()
    core.quit()
        
    

if __name__ == "__main__":
    main()
