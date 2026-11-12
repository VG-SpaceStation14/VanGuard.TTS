import base64, os, io, sys, re
from dotenv import load_dotenv

load_dotenv()

import torch
import numpy as np
import soundfile as sf
from flask import Flask, request, jsonify, abort, send_from_directory
from werkzeug.exceptions import HTTPException

from src.SpeakerPatch import SpeakerPatch, GetAllSpeakers
from src.WarmUp import WarmUp
from src.SoundEffects import add_echo, add_radio_effect, add_robot, _run_ffmpeg

current_directory = os.path.abspath(os.path.dirname(__file__))
bin_directory = os.path.join(current_directory, 'bin')
os.environ['PATH'] = f"{bin_directory}:{os.environ['PATH']}"
sys.path.append(bin_directory)

torch.set_num_threads(int(os.environ.get("THREADS", os.environ.get("threads", "6"))))
deviceName = "cuda" if torch.cuda.is_available() else "cpu"
device = torch.device(deviceName)

ApiToken = os.environ.get("API_TOKEN", os.environ.get("apitoken", "test"))
ServerPort = int(os.environ.get("PORT", "5000"))

os.makedirs('models', exist_ok=True)
local_file = 'models/v5_cis_base_nostress.pt'

if not os.path.isfile(local_file):
    print("Start download Silero V5 CIS Base (nostress)")
    torch.hub.download_url_to_file(
        'https://models.silero.ai/models/tts/ru/v5_cis_base_nostress.pt',
        local_file
    )

model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
model.to(device)

app = Flask(__name__, static_folder='www')

@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify({
        "error": e.name,
        "description": e.description
    }), e.code

speakers = model.speakers

@app.route('/')
def index():
    return send_from_directory('www', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('www', path)

@app.route('/voices')
def api_voices():
    return jsonify(GetAllSpeakers(speakers))

@app.route('/health', methods=['GET'])
def doHEALTH():
    return "OK"

def clean_ssml(ssml_text):
    return re.sub(r'\s*volume="[^"]*"', '', ssml_text)

def normalize_audio(audio):
    if isinstance(audio, torch.Tensor):
        audio_np = audio.detach().cpu().numpy()
    else:
        audio_np = np.asarray(audio)

    audio_np = audio_np.astype(np.float32).flatten()
    if audio_np.size == 0:
        return audio_np

    peak = np.max(np.abs(audio_np))
    if peak > 0:
        audio_np = audio_np / peak * 0.95
    return audio_np

def apply_loudnorm(input_buffer, sample_rate=24000, output_format='ogg'):
    input_buffer.seek(0)
    cmd = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
        '-i', 'pipe:0',
        '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11',
        '-ar', str(sample_rate),
        '-ac', '1',
        '-f', output_format, 'pipe:1'
    ]
    out = _run_ffmpeg(cmd, input_buffer.read())
    result = io.BytesIO(out)
    result.seek(0)
    return result

@app.route('/tts', methods=['POST'])
def doTTS():
    req = request.json
    if 'api_token' not in req:
        abort(400, description="Missing api_token")
        return
    if req['api_token'] != ApiToken:
        abort(403)
        return
    if 'text' not in req:
        abort(400, description="Missing text")
        return
    if 'speaker' not in req:
        abort(400, description="Missing speaker")
        return

    speaker = req['speaker']
    if 'sample_rate' not in req:
        req['sample_rate'] = 24000
    if 'format' not in req:
        req['format'] = 'ogg'

    speaker, voiceFile = SpeakerPatch(speaker, speakers)

    if req.get('ssml', False):
        cleaned_text = clean_ssml(req['text'])
        audio = model.apply_tts(
            ssml_text=cleaned_text,
            speaker=speaker,
            sample_rate=req['sample_rate'],
            voice_path=voiceFile
        )
    else:
        audio = model.apply_tts(
            text=req['text'],
            speaker=speaker,
            sample_rate=req['sample_rate'],
            voice_path=voiceFile
        )

    audio = normalize_audio(audio)

    with io.BytesIO() as buffer_:
        if req["format"] == "ogg":
            sf.write(buffer_, audio, req['sample_rate'], format="ogg", subtype="VORBIS")
        else:
            sf.write(buffer_, audio, req['sample_rate'], format=req["format"])
        buffer_.seek(0)

        effect = req.get('effect', None)
        if effect == "Echo":
            buffer_ = add_echo(buffer_, output_format=req["format"])
        elif effect == "Radio":
            buffer_ = add_radio_effect(buffer_, req['sample_rate'], format=req["format"])
        elif effect == "Robot":
            buffer_ = add_robot(buffer_, req['sample_rate'], format=req["format"])

        buffer_ = apply_loudnorm(buffer_, req['sample_rate'], req["format"])

        return jsonify({'results': [{'audio': base64.b64encode(buffer_.getvalue()).decode()}]})

if __name__ == '__main__':
    WarmUp(model, speakers)
    app.run(host='0.0.0.0', debug=False, port=ServerPort)
