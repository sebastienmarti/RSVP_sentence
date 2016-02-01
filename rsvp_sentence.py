# -*- coding: utf-8 -*-
"""
First test with xp.
Tries to build an RSVP

"""
import expyriment as xp
import numpy as np
import pyaudio
import sys
from random import shuffle
import os
import wave

""" Parameters """
n_trial = 10
n_stim = 12
# duration_fix = np.random.randint(500, 800, (n_trial,1))
duration_fix = 500
duration_stim = 48
duration_blank = [16, 200]
duration_iti = 2000
duration_postRSVP = 800
duration_visibility = 2000
duration_audio = 5000
save_path = "C:\sm228108\Documents\sebastien2\Divers\Python\Task\data"

""" Creates an audio file for subjects response """
def RecordAudio(TRIAL_NUM, RECORD_SECONDS, PATH):
	chunk = 1024
	FORMAT = pyaudio.paInt16
	CHANNELS = 1
	RATE = 44100
	RECORD_SECONDS = RECORD_SECONDS/1000
	# PATH = "C:\sm228108\Documents\sebastien2\Divers\Python\Task"

	p = pyaudio.PyAudio()

	stream = p.open(format=FORMAT,
	                channels=CHANNELS, 
	                rate=RATE, 
	                input=True,
	                output=True,
	                frames_per_buffer=chunk)

	print "* recording"
	frames = []
	for i in range(0, 44100 / chunk * RECORD_SECONDS):
	    data = stream.read(chunk)
	    frames.append(data)
	    # check for silence here by comparing the level with 0 (or some threshold) for 
	    # the contents of data.
	    # then write data or not to a file

	print "* done"

	stream.stop_stream()
	stream.close()
	p.terminate()

	# Write .wav file
	fn = str(TRIAL_NUM) + ".wav"
	wf = wave.open(os.path.join(PATH, fn), 'wb')
	wf.setnchannels(CHANNELS)
	wf.setsampwidth(p.get_sample_size(FORMAT))
	wf.setframerate(RATE)
	wf.writeframes(b''.join(frames))
	wf.close()
	return stream


""" Prepare experiment """
# creates matrix of sentences
with open("SentenceStim.txt") as f:
	words = [list(line.split()) for line in f]

# Initialize experiment
exp = xp.design.Experiment(name="rsvp_sentence", 
	foreground_colour = (255,255,255), background_colour = (0,0,0))
xp.control.set_develop_mode(False)
xp.control.initialize(exp)

Block1 = xp.design.Block("Test block 1")

# creates trials
all_trials = {}
d_blank = np.tile(duration_blank, (1,n_trial/2))
d_blank = d_blank[0]
shuffle(d_blank)
for itrl in range(n_trial):
	# Initialize trial
	all_trials[itrl] = xp.design.Trial()

	# fixation cross
	fixation = xp.stimuli.FixCross(size=(10,10))
	fixation.preload()

	all_stim = {} # create a dictionnary where to put stimuli
	sel = np.random.randint(len(words)) # randomly select one of the sentence
	for istim in range(n_stim):
		all_stim[istim] = xp.stimuli.TextLine(words[sel][istim], text_size=35) # create a stim for each word
		all_stim[istim].preload()

	# response screen 1
	resp = xp.stimuli.TextLine("Comprehension?")
	resp.preload()

	# response screen 2
	audio = xp.stimuli.TextLine("Sentence?")
	audio.preload()

	# inter trial
	iti = xp.stimuli.BlankScreen()
	iti.preload()

	# adding stimuli to trial
	all_trials[itrl].add_stimulus(fixation) # fixation
	for istim in range(n_stim):
		all_trials[itrl].add_stimulus(all_stim[istim]) # RSVP
	all_trials[itrl].add_stimulus(resp) # response screen
	all_trials[itrl].add_stimulus(audio) # audio screen

	# adding trials to block
	Block1.add_trial(all_trials[itrl])

# trial randomization 
Block1.shuffle_trials()
exp.add_block(Block1)

""" Loop for presentation """
trial_num=0
xp.control.start(exp)
for block in exp.blocks:
    for trial in block.trials:
        trial.stimuli[0].present()
        exp.clock.wait(duration_fix)
        # RSVP
    	for stim in range(1,n_stim+1):
    		trial.stimuli[stim].present()
    		exp.clock.wait(duration_stim)
    		trial.stimuli[0].present()
    		exp.clock.wait(d_blank[trial_num])
    	
    	# post RSVP
    	trial.stimuli[0].present()
        exp.clock.wait(duration_postRSVP)

    	# Response screen
    	trial.stimuli[n_stim+1].present()
    	key, rt = exp.keyboard.wait(duration=duration_visibility)
        exp.data.add([block.name, trial.id, key, rt, 
        	trial_num, d_blank[trial_num]])
        trial.stimuli[n_stim+2].present()
        audio_stream = RecordAudio(trial_num, duration_audio, save_path)
        exp.clock.wait(100)
    	iti.present()
    	exp.clock.wait(duration_iti)
    	trial_num = trial_num+1

xp.control.end()
