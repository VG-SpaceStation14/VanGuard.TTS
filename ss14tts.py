import base64, os, io, sys
import torch
import soundfile as sf
from flask import Flask, request, jsonify, abort, send_from_directory
from werkzeug.exceptions import HTTPException

from src.SpeakerPatch import SpeakerPatch, GetAllSpeakers
from src.WarmUp import WarmUp
from src.SoundEffects import add_echo, add_radio_effect, add_robot

current_directory = os.path.abspath(os.path.dirname(__file__))
bin_directory = os.path.join(current_directory, 'bin')
os.environ['PATH'] = f"{bin_directory}:{os.environ['PATH']}"
sys.path.append(bin_directory)

torch.set_num_threads(int(os.environ.get("threads", "6")))
deviceName = "cuda" if torch.cuda.is_available() else "cpu"
device = torch.device(deviceName)

ApiToken = os.environ.get("apitoken", "test")

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

    audio = model.apply_tts(
        text=req['text'],
        speaker=speaker,
        sample_rate=req['sample_rate']
    )

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

        return jsonify({'results': [{'audio': base64.b64encode(buffer_.getvalue()).decode()}]})

if __name__ == '__main__':
    WarmUp(model, speakers)
    app.run(host='0.0.0.0', debug=False, port=int(os.environ.get("PORT", "5000")))
