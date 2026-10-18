TITLE = 'Wave Studio'
SUBTITLE = 'A workbench for wave experiments'
READY = 'Press Run to start the experiment.'
CHANGED = 'Setup changed. Press Run to begin a fresh experiment.'
MEASUREMENTS = 'No measurements in this experiment.'
PAUSE_TO_EDIT = 'Pause the experiment to edit its physical setup.'
COMPUTE_MODE_TOOLTIPS = {
    'Economical': 'Limits computation to about 240 steps/s to reduce power use. Same numerical accuracy.',
    'Performance': 'Runs as fast as possible, using more power. Same numerical accuracy.',
}
COMPUTE_MODE_TOOLTIP = '\n'.join(f'{mode}: {text}' for mode,text in COMPUTE_MODE_TOOLTIPS.items())
