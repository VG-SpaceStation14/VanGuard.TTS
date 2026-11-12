from datetime import datetime

example_text = "В недрах тундры выдры в гетрах тырят в вёдра ядра кедров."

def WarmUp(model, speakers):
    print("WarmUp!")
    for idx, speaker in enumerate(speakers):
        if speaker == 'random':
            continue
        print("speaker: " + speaker)
        start_time = datetime.now()
        model.apply_tts(
            text=example_text,
            speaker=speaker,
            sample_rate=24000
        )
        end_time = datetime.now()
        print('speaker: {} done: {}'.format(speaker, end_time - start_time))
