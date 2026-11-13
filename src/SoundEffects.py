import subprocess
import io

RADIO1_PATH = "assets/radio1.wav"
RADIO2_PATH = "assets/radio2.wav"

def _run_ffmpeg(cmd, input_data):
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate(input=input_data)
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg error: {stderr.decode()}")
    return stdout

def pitch_shift(input_buffer, pitch_factor, sample_rate=24000, output_format='ogg'):
    if not 0.5 <= pitch_factor <= 2.0:
        raise ValueError("pitch_factor must be between 0.5 and 2.0")
        
    input_buffer.seek(0)

    shifted_rate = int(round(sample_rate * pitch_factor))
    tempo = 1.0 / pitch_factor
    
    cmd = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
        '-i', 'pipe:0',
        '-af', f'asetrate={shifted_rate},atempo={tempo:.8f}',
        '-ar', str(sample_rate),
        '-ac', '1',
        '-f', output_format, 'pipe:1'
    ]
    output = _run_ffmpeg(cmd, input_buffer.read())
    result = io.BytesIO(output)
    result.seek(0)
    return result

def add_echo(input_buffer, sample_rate=24000, output_format='ogg'):
    input_buffer.seek(0)
    cmd = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
        '-i', 'pipe:0',
        '-i', 'assets/announce.wav',
        '-filter_complex',
        f'[1:a]aresample={sample_rate},aformat=sample_fmts=fltp:channel_layouts=mono[ann];'
        f'[0:a][ann]afir=dry=10:wet=10[reverb];'
        f'[0:a][reverb]amix=inputs=2:weights=\'10 1\'[out]',
        '-map', '[out]',
        '-f', output_format, 'pipe:1'
    ]
    output = _run_ffmpeg(cmd, input_buffer.read())
    result = io.BytesIO(output)
    result.seek(0)
    return result

def add_radio_effect(input_buffer, hz=44100, format='ogg'):
    input_buffer.seek(0)
    input_data = input_buffer.read()

    cmd_filter = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
        '-i', 'pipe:0',
        '-af', 'highpass=f=1000,lowpass=f=3000,acrusher=level_in=1:level_out=1:bits=8:mode=0:aa=1',
        '-ar', str(hz),
        '-ac', '1',
        '-f', 's16le', 'pipe:1'
    ]
    filtered = _run_ffmpeg(cmd_filter, input_data)

    cmd_mix = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
        '-i', RADIO1_PATH,
        '-f', 's16le', '-ar', str(hz), '-ac', '1', '-i', 'pipe:0',
        '-i', RADIO2_PATH,
        '-filter_complex',
        '[0:a][1:a][2:a]concat=n=3:v=0:a=1[outa]',
        '-map', '[outa]',
        '-f', format,
        'pipe:1'
    ]

    result_bytes = _run_ffmpeg(cmd_mix, filtered)
    result = io.BytesIO(result_bytes)
    result.seek(0)
    return result

def add_robot(input_buffer, hz=44100, format='ogg'):
    input_buffer.seek(0)
    cmd = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
        '-i', 'pipe:0',
        '-filter:a', "afftfilt=real='hypot(re,im)*sin(0)':imag='hypot(re,im)*cos(0)':win_size=1024:overlap=0.5",
        '-ar', str(hz),
        '-ac', '1',
        '-f', format, 'pipe:1'
    ]
    output = _run_ffmpeg(cmd, input_buffer.read())
    result = io.BytesIO(output)
    result.seek(0)
    return result
