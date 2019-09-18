# -*- coding: utf-8 -*-
"""
TODO:
 * Nothing :-)
"""

# Imports stuff we need
import random
import glob
import copy
import quadro
import ppc
from psychopy import visual, event, sound, core, gui


# Appearance
GRID_ROWS = 3
GRID_COLS = 3
GRID_CELLSIZE = 1  # In degrees visual angle
STIM_SIZE = 0.8  # In degrees visual angle
FEEDBACK_ARGS = {
    'position': {'text': 'Placering\n       \u2191', 'pos': (0, 2.1)},  # Up
    'sound': {'text': '  \u2193\nLyd', 'pos': (0, -2)},  # Down
    'figure': {'text': '<--', 'pos': (-2.4, 0)},  # Left
    'color': {'text': '--> Farve', 'pos': (2.4, 0)}  # Right
}
FEEDBACK_COLORS = {
    1: 'green',  # Correct
    0: 'red',  # Wrong
    '': 'gray',  # Not scored
    'response': 'white'
}


# Durations
VISUAL_DURATION = 0.5  # Seconds
RESPONSE_WINDOW = {1: 2, 2: 2, 3:3, 4:3}  # key:value is factor: seconds
FEEDBACK_DURATION = 0.5  # Seconds

# Sequence properties
NONTARGETS_PER_BLOCK = {'pretest': 45, 'posttest': 45, 'training': 45, 'practice': 22}
TARGETS_PER_BLOCK = {'pretest': 15, 'posttest': 15, 'training': 15, 'practice': 8}
MAX_CONSECUTIVE_TARGETS = 2  # No more than this number of targets in a row
BREAK_INTERVAL = 30  # How frequently to add breaks during training
TRAINING_BLOCKS = 4  # Number of blocks to run during training

# Response stuff. Must match 
RESPONSE_KEYS = {'up': 'position', 
            'down': 'sound',
            'left': 'figure',
            'right': 'color'
}
QUIT_KEYS = ['escape']
CONTINUE_KEYS = ['return', 'enter']


# Features
features = {
    'position': [4,0,1,2,3,5,6,7,8],  # Ids of grid_coords
    'sound': glob.glob('sounds/*.wav'),
    'figure': ['circle', 'triangle', 'square', 'star'],  # Must match "figure_stims" dict
    'color': ['white', 'red', 'blue', 'green', 'dimgray', 'darkorange', 'yellow']
}

# Instruction stuff
INSTRUCTION_SALIENT_HEIGHT = 0.5
INSTRUCTION_HEIGHT = 0.3  # Text height in degrees visual angle
INSTRUCTION_POS = (0, 4)  # Middle of text in degrees angle
instructions = {
    'welcome': 'Tak fordi du ville hjælpe os, i vores undersøgelse!\nDu skal tage nogle forskellige variationer af en korttidshukommelsestest, der kaldes “N-back”. Du bliver gentagende gange præsenteret for en gruppe stimuli (form, farve, lyd, placering) i et par sekunder, og skal huske hvorvidt dele af den stimuli er den samme som noget du er blevet præsenteret for, enten 1 eller 2 sekvenser, tidligere. Du vil løbende blive introduceret for forskellige typer af denne opgave, hvor farve, form, position og lyd vil blive præsenteret i forskellige kombinationer. Det vil fremgå før hver opgave.\n\nTryk ENTER for at gå i gang!',
    
    'p1': 'Hvis du f.eks. bliver præsenteret for en cirkel oppe i venstre hjørne, hvorefter du igen bliver præsenteret for en cirkel oppe i venstre hjørne, skal du markere at PLACERING gik igen fra forrige stimuli. Dette gør du ved at klikke på knappen [ ↑ ] på tastaturet.\nOmvendt, hvis du f.eks. bliver præsenteret for en cirkel oppe i venstre hjørne, hvorefter du bliver præsenteret for en cirkel nede i højre hjørne, skal du markere at PLACERING ikke gik igen fra forrige stimuli. Dette gør du ved at IKKE at trykke på noget.\n\nTryk ENTER for at fortsætte!',
    'f2': 'Den følgende opgave minder meget om den forrige. Denne gang er placering hele tiden den samme, men du skal i stedet markere når FORMEN gentages. Dette gør du ved at klikke på knappen [ <-- ] på tastaturet.\nDenne gang skal du dog huske om FORMEN er den samme som den form der var for 2 gange siden.\nDette ændrer sig et par gange i løbet af undersøgelsen, så husk at hold øje med informationen i bunden, der viser dig hvor mange gange du skal huske tilbage.\n\nTryk ENTER for at starte opgaven!',
    'sc2': 'Denne gang skal du både markere FARVE og LYD. Du skal huske 2 gange tilbage. FARVE markeres ved at klikke på knappen [ --> ] på tastaturet, og LYD markeres ved at klikke på knappen [ ↓ ].\n\nTryk ENTER for at starte opgaven!',
    'pcfs1': 'I næste opgave introducerer vi endnu en ændring af opgaven. Denne gang skal du markere alle fire faktorer. Du skal nu huske 1 gang tilbage.\nTryk ENTER for at starte opgaven!',
    
    'pretest': 'Den egentlige undersøgelse går i gang nu, og du vil derfor ikke længere få feedback på dine svar. Husk at holde øje med informationen i bunden, da det nogle gange ændrer sig, om du skal huske 1 eller 2 gange tilbage.\n\nTryk ENTER for at fortsætte!',
    'posttest': 'I den næste række opgaver får du ikke længere feedback på dine svar. Husk stadig at holde øje med informationen i bunden, da det nogle gange ændrer sig, om du skal huske 1 eller 2 gange tilbage.\n\nTryk ENTER for at fortsætte!',
    
    'pc2': 'XXX',
    'fc2': 'XXX',
    'pcs1': 'XXX',
    'fcs1': 'XXX',
    
    'training_train': 'I følgende opgave får du feedback på din performance. Når man får feedback på sine opgaver, kan man forbedre sig hurtigere. Dit mål er altså at bruge denne feedback på at se hvor meget du kan forbedre dig i denne opgave.\n\nTryk ENTER for at fortsætte!',
    'training_transfer': 'I følgende opgave får du feedback på din performance. Når man får feedback på sine opgaver, kan man forbedre sig hurtigere. Dit mål er altså at bruge denne feedback til at se hvor meget du kan forbedre dig i denne opgave. Efter denne opgave vil du skulle tage de samme opgaver igen, som du lige har taget (igen uden feedback).\n\nUdover at se hvor meget du kan forbedre dig i denne opgave, så skal du ligeledes bruge denne opgave til at forbedre dig i de opgaver, du lige har været igennem. Det er derfor vigtigt, at du hele tiden har fokus på, hvordan du kan relatere det, du lærer nu, til de opgaver, du gennemførte i starten af denne session.\n\nTryk ENTER for at fortsætte!',
    'training_start': 'Gør klar til at starte.',
    
    #'break': 'Nu kommer der en pause! Det er vigtigt for undersøgelsen, at du holder dig fokuseret hele vejen igennem. \n\nTryk ENTER for at fortsætte!',
    'bye': 'Tak for din deltagelse! Du behøver ikke at lukke programmet ned, men du bedes i stedet efterlade computeren som den er, og så er du velkommen til at komme ud af rummet.',
    'N': 'Husk %i %s tilbage.',
    'status': '\n\nStatus: %i %% færdig.',
    'training_feedback': 'Du ramte %i%% af målene.\nDu trykkede på %i%% af ikke-målene.\n\nTryk ENTER for at gøre klar til næste del.'
}


"""
DIALOGUE AND SOME STUFF
"""
DIALOGUE = {
    'id': '',
    'gender': ['female', 'male'],
    'instruction': ['training_train', 'training_transfer'],
    'age': '',
    'simulate': ['no', 'yes'],
    'occupation': ['studerende i arbejde', 'ledig']
}
if not gui.DlgFromDict(DIALOGUE).OK:
    core.quit()

# Fix a bug in PsychoPy3 where strings are lists of characters
for key, value in DIALOGUE.items():
    if isinstance(value, list):
        DIALOGUE[key] = ''.join(value)

if DIALOGUE['simulate'] == 'yes':
    VISUAL_DURATION = 0.02
    RESPONSE_WINDOW = {1:0.02, 2:0.02, 3:0.02, 4:0.02}
    FEEDBACK_DURATION = 0.02

# Make coordinates for grid
grid_data = quadro.makeGrid(rows=GRID_ROWS, cols=GRID_COLS, size=GRID_CELLSIZE)
grid_coords = grid_data['positions']

# Set up writer
writer = ppc.csv_writer(folder='data', column_order=['id', 'gender', 'age', 'instruction', 'phase', 'task', 'factor', 'N', 'trial', 'position', 'color', 'figure', 'sound'])

"""
STIMULI
"""

# Setup the window, grid, marker in the grid, text-field and some clocks
win = visual.Window(size=[1000, 1000], fullscr=False, monitor='testMonitor', color='black', allowGUI=True, units='deg')
grid = visual.ShapeStim(win=win, lineWidth=2, lineColor='white', closeShape=False, interpolate=False, vertices=grid_data['vertices'])
instruction = visual.TextStim(win, height=INSTRUCTION_HEIGHT, pos=INSTRUCTION_POS)
feedback_texts = {feature: visual.TextStim(win, height=0.4, color=FEEDBACK_COLORS[''], alignHoriz='center', **FEEDBACK_ARGS[feature]) for feature in features.keys()}
N_text = visual.TextStim(win, height=0.5, pos=(0, -4), text='')
clock = core.Clock()

# Load figures and sounds a priori
figure_args = {'fillColor': 'white', 'lineColor': None}
figure_stims = {
    'circle': visual.Circle(win, radius=STIM_SIZE/2, **figure_args),
    'triangle': visual.Polygon(win, edges=3, size=STIM_SIZE, **figure_args),
    'square': visual.Polygon(win, edges=4, size=STIM_SIZE, **figure_args),
    #'hexagon': visual.Polygon(win, edges=6, size=STIM_SIZE, **figure_args),
    'star': visual.ShapeStim(win, vertices=[(0, 1), (0.3, 0.3), (1, 0.15), (0.3, -0.3), (0.7, -1), (0, -0.65), (-0.7, -1), (-0.3, -0.3), (-1, 0.15), (-0.3, 0.3)], size=STIM_SIZE/2, **figure_args)
}
sounds = {name: sound.Sound(name) for name in features['sound']}

# Colors to be used for targets in the training_transfer group
color_targets = random.sample(features['color'], len(figure_stims))


"""
FUNCTIONS FOR TRIAL STRUCTURE
"""

def create_sequence(N, phase):
    """ Try making lists until a good one is found """
    while True:
        # Create a candidate list
        candidate = [0] * NONTARGETS_PER_BLOCK[phase] + [1] * TARGETS_PER_BLOCK[phase]  # Correct number of targets and fillers
        random.shuffle(candidate)  # Random order
        candidate = [0] * N + candidate
        
        # Check that it fulfills the criterion
        needle = '1' * (MAX_CONSECUTIVE_TARGETS + 1)
        if not quadro.find_sublist(candidate, needle):
            return(candidate)


def get_stimulus(target, nback, stimuli):
    """
    Returns n-back stimulus if target. 
    Returns a non-nback stimulus if not target.
    """
    if target:
        # If target, simply return it
        return(nback)
    else:
        # Remove target from all stimuli to get a list of nontargets
        nontargets = copy.copy(stimuli)
        nontargets.remove(nback)
        
        # ... and return one of those nontargets
        return(random.choice(nontargets))


def make_trials(N, block_features, phase, task):
    """ Make a list of trials (dicts)"""
    trials = list()
    
    # Sequences for all block_features
    sequences = {name: create_sequence(N, phase) for name in block_features}
    
    # Loop and create trials
    for i in range(len(create_sequence(N, phase))):
        
        trial = {
            # Meta
            'factor': len(block_features),  # How many features
            'N': N,  # N-back
            'trial': i + 1,  # To keep track of "time"
            'phase': phase,
            'task': task
        }
        
        # Add 'feature_target' and 'feature' keys+values for each feature.
        for feature in features.keys():
            # Placeholders for responses
            trial[feature + '_response'] = ''
            trial[feature + '_score'] = ''
            
            # Depends on (1) if this is a varying feature, (2) if this a lead-in trial and (3) 
            if feature in block_features:
                trial[feature + '_tested'] = 1
                trial[feature + '_target'] = sequences[feature][i]
                if i < N:
                    # Just pick at random
                    trial[feature] = random.choice(features[feature])
                else:
                    # Pick depending on target
                    trial[feature] = get_stimulus(
                        target = sequences[feature][i], 
                        nback = trials[-N][feature], 
                        stimuli = features[feature])
            # For untested features, the first feature is the "neutral" one
            else:
                trial[feature + '_target'] = ''
                trial[feature + '_tested'] = 0
                trial[feature] = features[feature][0]
                
                # No neutral sound if only sound
                if 'sound' not in block_features:
                    trial['sound'] = ''

        # Add the trial to the trial list
        trial.update(DIALOGUE)
        trials.append(trial)
    
    return(trials)


def show_training_feedback(trials, features):
    # Collect scores
    hits = []
    fas = []
    for trial in trials:
        for feature in features:
            if trial[feature + '_target'] == 1:
                hits.append(trial[feature + '_score'])
            else:
                fas.append(trial[feature + '_score'])
    
    # Compute summaries in percent
    hit_rate = 100*sum(hits)/len(hits)
    fa_rate = 100*(1 - sum(fas)/len(fas))
    
    # Show feedback
    feedback = instructions['training_feedback'] %(hit_rate, fa_rate)
    show_salient_instruction(feedback)

"""
FUNCTIONS FOR STIMULUS PRESENTATION
"""

def show_instruction(text):
    """ Show a text, wait for key press and return the key"""
    # Show instruction
    instruction.text = text + instructions['status'] %(round(100*cumulative_trials / total_trials))
    instruction.draw()
    win.flip()
    
    # Wait for the response (return None)
    if DIALOGUE['simulate'] == 'no':
        event.waitKeys(keyList=CONTINUE_KEYS)


def show_salient_instruction(text):
    # Make more salient
    instruction.height = INSTRUCTION_SALIENT_HEIGHT
    instruction.pos = (0, 0)
    instruction.color = 'yellow'
    instruction.bold = True
    grid.autoDraw = False
    
    # Show it
    show_instruction(text)
    
    # Back to normal
    instruction.height = INSTRUCTION_HEIGHT
    instruction.pos = INSTRUCTION_POS
    instruction.color = 'white'
    instruction.bold = False
    grid.autoDraw = True


def nice_quit():
    """ Quits nicely """
    win.close()
    core.quit()


def draw_feedback(trial):
    """ Draw feature texts with correct feedback color """
    for feature in features:
        # Only show instructions for tested features
        if trial[feature + '_tested']:
            feedback_text = feedback_texts[feature]  # Convenient
            
            # Only show feedbacl during practice and training
            if trial['phase'] in ('practice', 'training'):
                # Color according to score
                feedback_text.color = FEEDBACK_COLORS[trial[feature + '_score']]
                
                # ... except for correct rejections (just to make it easier to process)
                if trial[feature + '_target'] == 0 and trial[feature + '_score'] == 1:
                    feedback_text.color = FEEDBACK_COLORS['']
            # If not explicit feedback, at least show that a response was collected
            elif trial[feature + '_response']:
                feedback_text.color = FEEDBACK_COLORS['response']
                
            # Draw it and return text color to normal
            feedback_text.draw()
            feedback_text.color = FEEDBACK_COLORS['']


def draw_trial(trial, targets=True):
    """ Draw grid, response options (with feedback), N, targets (optional). """
    grid.draw()
    draw_feedback(trial)
    N_text.draw()
    
    # Optionally draw targets
    if targets and trial['phase'] == 'training' and trial['instruction'] == 'training_transfer':
        for i, figure in enumerate(figure_stims.values()):
            figure.pos = (i - (len(figure_stims) - 1)/2, 5)  # Centered
            figure.fillColor = color_targets[i]
            figure.draw()


def run_block(N, features, phase, task):
    """ Run the experiment for a trial list """
    global cumulative_trials
    trials = make_trials(N, features, phase, task)
    
    # Show instruction
    N_text.text = instructions['N'] % (N, 'sekvenser' if N > 1 else 'sekvens')
    draw_trial(trials[0], targets=False)
    
    # Show task instructions.
    if phase != 'training':
        show_instruction(instructions[task])
    else:
        # During training, the instructions have already been shown.
        show_instruction(instructions['training_start'])
        
    # Show trials
    for trial in trials:
        # Prepare stimuli
        draw_trial(trial)
        
        figure = figure_stims[trial['figure']]
        figure.fillColor = trial['color']
        figure.pos = grid_coords[trial['position']]
        figure.draw()
        
        # Show it
        win.flip()
        if trial['sound_tested']:
            sounds[trial['sound']].play()
        clock.reset()
        event.clearEvents()

        # Control stimulus offset and responses
        flipped = False
        while clock.getTime() < RESPONSE_WINDOW[trial['factor']]:
            # Stimulus offset
            if clock.getTime() > VISUAL_DURATION and not flipped:
                draw_trial(trial)
                win.flip()
                flipped = True
            
            # Collect response and score it
            if DIALOGUE['simulate'] == 'no':
                responses = event.getKeys(keyList=RESPONSE_KEYS.keys())
            else:
                responses = [random.choice(list(RESPONSE_KEYS.keys()))]
            if responses:
                for response in responses:
                    response_feature = RESPONSE_KEYS[response]
                    if response_feature in features:
                        trial[response_feature + '_response'] = 1
                        trial[response_feature + '_score'] = int(trial[response_feature + '_target'] == 1)
                
                draw_trial(trial)
                win.flip()
            
            # Save on computer ressources. RT is not important
            core.wait(0.1, hogCPUperiod=0)
        
        
        # End of trial. Check for CR and misses
        for feature in features:
            if trial[feature + '_response'] == '':
                trial[feature + '_response'] = 0
                trial[feature + '_score'] = int(trial[feature + '_target'] == trial[feature + '_response'])

        # Save this trial immediately
        writer.write(trial)
        writer.flush()
        
        # ... and give feedback
        draw_trial(trial)
        win.flip()
        core.wait(FEEDBACK_DURATION)
        
        # Quit and count
        cumulative_trials += 1
        if event.getKeys(keyList=QUIT_KEYS):
            nice_quit()
        
    # Performance summary after each training block
    if phase == 'training':
        show_training_feedback(trials, features)


def run_test(phase):
    """ Runs the tests in the desired order. """   
    show_instruction(instructions[phase])
    
    run_block(N=2, features=['position', 'color'], phase=phase, task='pc2')
    run_block(N=2, features=['figure', 'color'], phase=phase, task='fc2')
    
    run_block(N=1, features=['position', 'color', 'sound'], phase=phase, task='pcs1')
    run_block(N=1, features=['figure', 'color', 'sound'], phase=phase, task='fcs1')
    
    run_block(N=1, features=['position', 'color', 'figure', 'sound'], phase=phase, task='pcfs1')


"""
RUN IT
"""
# Total number of trials. Update this when changing the procedure
cumulative_trials = 0
total_trials = (NONTARGETS_PER_BLOCK['practice'] + TARGETS_PER_BLOCK['practice'] + 1.5) * 4 + \
    (NONTARGETS_PER_BLOCK['pretest'] + TARGETS_PER_BLOCK['pretest'] + 1.5) * 5 + \
    (NONTARGETS_PER_BLOCK['posttest'] + TARGETS_PER_BLOCK['posttest'] + 1.5) * 5 + \
    (NONTARGETS_PER_BLOCK['training'] + TARGETS_PER_BLOCK['training'] + 2) * TRAINING_BLOCKS

# Pretest
show_instruction(instructions['welcome'])

# Practice
run_block(N=1, features=['position'], phase='practice', task='p1')
run_block(N=2, features=['figure'], phase='practice', task='f2')
run_block(N=2, features=['sound', 'color'], phase='practice', task='sc2')
run_block(N=1, features=['position', 'color', 'figure', 'sound'], phase='practice', task='pcfs1')

# Pretest
run_test('pretest')

# Training instruction
show_salient_instruction(instructions[DIALOGUE['instruction']])

# Training
for block in range(TRAINING_BLOCKS):
    run_block(N=2, features=['position', 'sound'], phase='training', task='ps2')

# Posttest
run_test('posttest')

# Goodbye
show_instruction(instructions['bye'])
nice_quit()
