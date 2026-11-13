import base64, os, io, sys, re
import xml.etree.ElementTree as ET
import warnings
from dotenv import load_dotenv

warnings.filterwarnings("ignore", category=SyntaxWarning)

load_dotenv()

import torch
import numpy as np
import soundfile as sf
from flask import Flask, request, jsonify, abort, send_from_directory
from werkzeug.exceptions import HTTPException

from src.SpeakerPatch import SpeakerPatch, GetAllSpeakers
from src.WarmUp import WarmUp
from src.SoundEffects import add_echo, add_radio_effect, add_robot, pitch_shift

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

local_file = 'models/v5_6_ru.pt'

if not os.path.isfile(local_file):
    print("Start download Silero V5 6 RU (latest Russian model)")
    torch.hub.download_url_to_file(
        'https://models.silero.ai/models/tts/ru/v5_6_ru.pt',
        local_file
    )

model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
model.to(device)

SYNTHETIC_VOICES = {
    "aidar_deep": ("aidar", 0.94), "aidar_low": ("aidar", 0.97), "aidar": ("aidar", 1.0), "aidar_high": ("aidar", 1.06), "aidar_veryhigh": ("aidar", 1.12),
    "eugene_deep": ("eugene", 0.94), "eugene_low": ("eugene", 0.97), "eugene": ("eugene", 1.0), "eugene_high": ("eugene", 1.06), "eugene_veryhigh": ("eugene", 1.12),
    "baya_deep": ("baya", 0.88), "baya_low": ("baya", 0.94), "baya": ("baya", 1.0), "baya_high": ("baya", 1.06), "baya_veryhigh": ("baya", 1.12),
    "kseniya_deep": ("kseniya", 0.88), "kseniya_low": ("kseniya", 0.94), "kseniya": ("kseniya", 1.0), "kseniya_high": ("kseniya", 1.06), "kseniya_veryhigh": ("kseniya", 1.12),
    "xenia_deep": ("xenia", 0.88), "xenia_low": ("xenia", 0.94), "xenia": ("xenia", 1.0), "xenia_high": ("xenia", 1.06), "xenia_veryhigh": ("xenia", 1.12),
}

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
    base_voices = GetAllSpeakers(speakers)
    all_voices = list(set(base_voices + list(SYNTHETIC_VOICES.keys())))
    return jsonify(sorted(all_voices))

@app.route('/health', methods=['GET'])
def doHEALTH():
    return "OK"

def clean_ssml(ssml_text):
    try:
        if not ssml_text.strip().startswith("<speak>"):
            ssml_text = f"<speak>{ssml_text}</speak>"
            
        root = ET.fromstring(ssml_text)

        def flatten_ssml(node, current_rate="medium", current_pitch="medium"):
            if 'rate' in node.attrib:
                current_rate = node.attrib['rate']
                
            if 'pitch' in node.attrib:
                p = node.attrib['pitch']
                if p.startswith('+'):
                    current_pitch = 'high'
                elif p.startswith('-'):
                    current_pitch = 'low'
                elif p.endswith('%'):
                    current_pitch = 'high'
                else:
                    current_pitch = p

            if node.tag == 'break':
                yield f'<break time="{node.attrib.get("time", "400ms")}"/>'
                return

            if node.text and node.text.strip():
                text = node.text.strip()
                if current_rate != "medium" or current_pitch != "medium":
                    yield f'<prosody rate="{current_rate}" pitch="{current_pitch}">{text}</prosody>'
                else:
                    yield text

            for child in node:
                yield from flatten_ssml(child, current_rate, current_pitch)
                
                if child.tail and child.tail.strip():
                    tail_text = child.tail.strip()
                    if current_rate != "medium" or current_pitch != "medium":
                        yield f'<prosody rate="{current_rate}" pitch="{current_pitch}">{tail_text}</prosody>'
                    else:
                        yield tail_text

        flat_parts = list(flatten_ssml(root))
        result = f"<speak>{''.join(flat_parts)}</speak>"
        
        return re.sub(r'\s+', ' ', result).strip()
        
    except Exception as e:
        print(f"SSML parse error: {e}")
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

@app.route('/tts', methods=['POST'])
def doTTS():
    try:
        req = request.json
        if 'api_token' not in req or req['api_token'] != ApiToken:
            abort(403)
            return
        if 'text' not in req:
            abort(400, description="Missing text")
            return
        if 'speaker' not in req:
            abort(400, description="Missing speaker")
            return

        requested_speaker = req['speaker']
        if 'sample_rate' not in req:
            req['sample_rate'] = 24000
        if 'format' not in req:
            req['format'] = 'ogg'

        pitch_factor = 1.0

        if requested_speaker in SYNTHETIC_VOICES:
            base_speaker, pitch_factor = SYNTHETIC_VOICES[requested_speaker]
            speaker = base_speaker
        else:
            speaker = requested_speaker

        speaker, voiceFile = SpeakerPatch(speaker, speakers)

        if req.get('ssml', False):
            cleaned_text = clean_ssml(req['text'])
            audio = model.apply_tts(
                ssml_text=cleaned_text,
                speaker=speaker,
                sample_rate=req['sample_rate'],
                voice_path=voiceFile,
                put_accent=True,
                put_yo=True
            )
        else:
            audio = model.apply_tts(
                text=req['text'],
                speaker=speaker,
                sample_rate=req['sample_rate'],
                voice_path=voiceFile,
                put_accent=True,
                put_yo=True
            )

        audio = normalize_audio(audio)

        with io.BytesIO() as buffer_:
            if req["format"] == "ogg":
                sf.write(buffer_, audio, req['sample_rate'], format="ogg", subtype="VORBIS")
            else:
                sf.write(buffer_, audio, req['sample_rate'], format=req["format"])
            buffer_.seek(0)

            if pitch_factor != 1.0:
                buffer_ = pitch_shift(buffer_, pitch_factor, req['sample_rate'], req["format"])

            effect = req.get('effect', None)
            if effect == "Echo":
                buffer_ = add_echo(buffer_, sample_rate=req['sample_rate'], output_format=req["format"])
            elif effect == "Radio":
                buffer_ = add_radio_effect(buffer_, req['sample_rate'], format=req["format"])
            elif effect == "Robot":
                buffer_ = add_robot(buffer_, req['sample_rate'], format=req["format"])

            return jsonify({'results': [{'audio': base64.b64encode(buffer_.getvalue()).decode()}]})
            
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal Server Error", "description": str(e)}), 500

if __name__ == '__main__':
    import socket
    
    class FilteredStderr:
        def __init__(self, original):
            self.original = original
            self.warned = False
            
        def write(self, text):
            if "WARNING: This is a development server" in text:
                if not self.warned:
                    YELLOW = "\033[93m"
                    CYAN = "\033[96m"
                    GREEN = "\033[92m"
                    RESET = "\033[0m"
                    
                    try:
                        hostname = socket.gethostname()
                        local_ip = socket.gethostbyname(hostname)
                    except:
                        local_ip = "127.0.0.1"
                        
                    self.original.write(f"\n{GREEN} * [VanGuard TTS] Успешный запуск сервера!{RESET}\n")
                    self.original.write(f"{YELLOW} * [VanGuard TTS] ВНИМАНИЕ: Вы запустили dev-сервер. Для продакшена используйте Gunicorn!{RESET}\n")
                    self.original.write(f"{CYAN} * [VanGuard TTS] Локальный доступ: http://127.0.0.1:{ServerPort}{RESET}\n")
                    if local_ip != "127.0.0.1":
                        self.original.write(f"{CYAN} * [VanGuard TTS] Сетевой доступ:  http://{local_ip}:{ServerPort}{RESET}\n")
                    self.original.write("\n")
                    self.warned = True
                return

            if " * Running on" in text or " * Serving Flask app" in text:
                return
                
            self.original.write(text)
            
        def flush(self):
            self.original.flush()
            
        def __getattr__(self, name):
            return getattr(self.original, name)

    original_stderr = sys.stderr
    sys.stderr = FilteredStderr(original_stderr)

    try:
        WarmUp(model, speakers)
        app.run(host='0.0.0.0', debug=False, port=ServerPort)
    finally:
        sys.stderr = original_stderr
