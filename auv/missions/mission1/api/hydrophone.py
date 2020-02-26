from soundcard.pulseaudio import *

spk = snd.get_speaker('USB')
spk = snd.default_speaker()

mic = snd.get_microphone('Mic')
