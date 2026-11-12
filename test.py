from ss14tts import model, speakers, add_echo, add_radio_effect, add_robot
import io
import soundfile as sf

example_text = "В недрах тундры выдры в гетрах тырят в вёдра ядра кедров."

audio = model.apply_tts(
    text=example_text,
    speaker="random",
    sample_rate=24000
)

buffer_ = io.BytesIO()
sf.write(buffer_, audio, 24000, format="ogg", subtype="VORBIS")
buffer_.seek(0)

buffer_ = add_echo(buffer_, output_format="ogg")
buffer_ = add_radio_effect(buffer_, 24000, format="ogg")
buffer_ = add_robot(buffer_, 24000, format="ogg")
