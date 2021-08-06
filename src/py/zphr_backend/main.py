from flask import Flask
from flask import request
import alsaaudio

app = Flask(__name__)


@app.route('/volDigital', methods=['POST', 'GET'])
def volume_digital():
    alsa_digital_mixer = alsaaudio.Mixer('Digital', 0, 0)
    if request.method == 'POST':
        vol: int = int(request.form['vol'])
        if vol > 100:
            vol = 100
        if vol < 0:
            vol = 0
        alsa_digital_mixer.setvolume(vol)
    return str(alsa_digital_mixer.getvolume()[0])


@app.route('/volHeadphone', methods=['POST', 'GET'])
def volume_headphone():
    alsa_headphone_mixer = alsaaudio.Mixer('Headphone', 0, 0)  # two zeroes needed because PulseAudio
    if request.method == 'POST':
        vol: int = int(request.form['vol'])
        if vol > 100:
            vol = 100
        if vol < 0:
            vol = 0
        alsa_headphone_mixer.setvolume(vol)
    return str(alsa_headphone_mixer.getvolume()[0])


@app.route('/mute', methods=['POST', 'GET'])
def mute():
    alsa_digital_mixer = alsaaudio.Mixer('Digital', 0, 0)
    if request.method == 'POST':
        digi_mute = 1
        if int(request.form['mute']) != 1:
            digi_mute = 0
        alsa_digital_mixer.setmute(digi_mute)
    return str(alsa_digital_mixer.getmute()[0])


@app.route('/analogBooster1', methods=['POST', 'GET'])
def analog_b1():
    alsa_ab1_mixer = alsaaudio.Mixer('Analogue', 0, 0)
    if request.method == 'POST':
        vol: int = int(request.form['vol'])
    return str(alsa_ab1_mixer.getvolume()[0])


@app.route('/analogBooster2', methods=['POST', 'GET'])
def analog_b2():
    alsa_ab2_mixer = alsaaudio.Mixer('Analogue Playback Boost', 0, 0)
    if request.method == 'POST':
        vol: int = int(request.form['vol'])
    return str(alsa_ab2_mixer.getvolume()[0])