import os
import glob

cwd = os.getcwd()
dynVoices = cwd + "/voices"

if not os.path.exists(dynVoices):
    os.makedirs(dynVoices)

def SpeakerPatchInit(model, example_text):
    pass

def GetAllSpeakers(speakers):
    voices = set()
    pt_files = glob.glob(os.path.join(dynVoices, "*.pt"))
    for pt in pt_files:
        voice_name = os.path.basename(pt).replace(".pt", "")
        voices.add(voice_name)
    for spk in speakers:
        if spk != 'random':
            voices.add(spk)
    return sorted(list(voices))

def SpeakerPatch(speaker, speakers):
    voiceFile = dynVoices + "/" + speaker + ".pt"
    if os.path.exists(voiceFile):
        return "random", voiceFile
    if speaker in speakers:
        return speaker, voiceFile
    default_speaker = next((s for s in speakers if s.startswith('ru_')), 'random')
    return default_speaker, voiceFile
