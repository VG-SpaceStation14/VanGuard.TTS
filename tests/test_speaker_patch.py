from src.SpeakerPatch import SpeakerPatch
from unittest.mock import patch

def test_custom_voice():
    speakers = ['aidar', 'random']
    with patch('os.path.exists', return_value=True):
        speaker, voice_file = SpeakerPatch("oleg", speakers)
        assert speaker == "random"
        assert voice_file.endswith("voices/oleg.pt")

def test_existing_voice():
    speakers = ['aidar', 'random']
    speaker, voice_file = SpeakerPatch("aidar", speakers)
    assert speaker == "aidar"

def test_fallback_voice():
    speakers = ['aidar', 'random']
    speaker, voice_file = SpeakerPatch("nonexistent_voice", speakers)
    assert speaker == "aidar"
