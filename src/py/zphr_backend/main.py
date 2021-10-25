"""

The Backend for ZeroPointHifiRemote, or ZPHR for short.
This module exposes a REST API offering control over audio settings and some handy system maintenance like reboots.
It is intended to assist a headless Linux DAC project, like Raspberry Pi + Hifiberry DAC
"""

from flask import Flask
from flask import request
from subprocess import run as subprun
import alsaaudio

app = Flask(__name__)



@app.route('/volDigital', methods=['POST', 'GET'])
def volume_digital():
    """

    Creates API an endpoint to get and set the "Digital" volume of a DAC in ALSA.
    The Getter uses HTTP GET and the Setter uses HTTP POST.
    Input is validated to be between 0 and 100.
    Returns:
        A string with the actual new volume as reported by ALSA.
    """
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
    """

    Creates an API endpoint to get and set the "Headphone" volume of a DAC in ALSA.
    The Getter uses HTTP GET and the Setter uses HTTP POST.
    Input is validated to be between 0 and 100.
    Returns:
        A string with the actual new volume as reported by ALSA.
    """
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
    """

    Creates an API endpoint to get and set the mute state of the "Digital" thingy of a DAC in ALSA.
    The Getter uses HTTP GET and the Setter uses HTTP POST.
    Input is validated to be either 0 or 1.
    Returns:
        A string with the actual new mute state as reported by ALSA
    """
    alsa_digital_mixer = alsaaudio.Mixer('Digital', 0, 0)
    if request.method == 'POST':
        digi_mute = 1
        if int(request.form['mute']) != 1:
            digi_mute = 0
        alsa_digital_mixer.setmute(digi_mute)
    else:
        return str(alsa_digital_mixer.getmute()[0])


@app.route('/analogBooster1', methods=['POST', 'GET'])
def analog_b1():
    """

    Creates an API endpoint to get and set the "Analogue Booster" 1 volume of a DAC in ALSA.
    The Getter uses HTTP GET and the Setter uses HTTP POST.
    Input is validated to be either 0 or 100.
    Returns:
        A string with the actual new volume as reported by ALSA.
"""
    alsa_ab1_mixer = alsaaudio.Mixer('Analogue', 0, 0)
    if request.method == 'POST':
        if int(request.form['vol']) > 0:
            alsa_ab1_mixer.setvolume(100)
        else:
            alsa_ab1_mixer.setvolume(0)
    return str(alsa_ab1_mixer.getvolume()[0])


@app.route('/analogBooster2', methods=['POST', 'GET'])
def analog_b2():
    """

    Creates an API endpoint to get and set the "Analogue Booster" 2 volume of a DAC in ALSA.
    The Getter uses HTTP GET and the Setter uses HTTP POST.
    Input is validated to be either 0 or 100.
    Returns:
        A string with the actual new volume as reported by ALSA.
"""
    alsa_ab2_mixer = alsaaudio.Mixer('Analogue Playback Boost', 0, 0)
    if request.method == 'POST':
        if int(request.form['vol']) > 0:
            alsa_ab2_mixer.setvolume(100)
        else:
            alsa_ab2_mixer.setvolume(0)
    return str(alsa_ab2_mixer.getvolume()[0])


@app.route('/reboot', methods=['GET'])
def system_reboot():
    """

    Creates an API endpoint to reboot the backend Host.
    A simple GET request will trigger a reboot after 5 seconds.
    Returns:
        The exit code of the shutdown command
    """
    return str(subprun(["sudo shutdown", "-r" "t 5"]).returncode)


@app.route('/shutdown', methods=['GET'])
def system_shutdown():
    """

    Creates an API endpoint to shut down the backend Host.
    A simple GET request will trigger a shutdown after 5 seconds.
    Returns:
        The exit code of the shutdown command
"""
    return str(subprun(["sudo shutdown", "-h", "t 5"]).returncode)
