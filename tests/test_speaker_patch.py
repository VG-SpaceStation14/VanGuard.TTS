from src.SpeakerPatch import SpeakerPatch

def test_custom_voice():
    speakers = ['ru_aigul', 'random']
    speaker, voice_file = SpeakerPatch("oleg", speakers)
    assert speaker == "random"
    assert voice_file.endswith("voices/oleg.pt")

def test_existing_voice():
    speakers = ['ru_aigul', 'random']
    speaker, voice_file = SpeakerPatch("ru_aigul", speakers)
    assert speaker == "ru_aigul"

def test_fallback_voice():
    speakers = ['ru_aigul', 'random']
    speaker, voice_file = SpeakerPatch("nonexistent_voice", speakers)
    assert speaker == "ru_aigul"
