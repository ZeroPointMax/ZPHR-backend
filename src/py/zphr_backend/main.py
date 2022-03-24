"""

The Backend for ZeroPointHifiRemote, or ZPHR for short.
This module exposes a REST API offering control over audio settings and some handy system maintenance like reboots.
It is intended to assist a headless Linux DAC project, like Raspberry Pi + Hifiberry DAC
"""

from flask import Flask
from flask import request
import alsaaudio
import subprocess
import re

app = Flask(__name__)

# RegEx to determine state of Bluetooth from rfkill output
re_bluetooth_unlocked = re.compile("(.*bluetooth.*hci.*)((unblocked unblocked)|(entsperrt entsperrt))")
re_bluetooth_locked = re.compile("(.*bluetooth.*hci.*)((blocked unblocked)|(gesperrt entsperrt))")
re_bluetooth_hwlock = re.compile("(.*bluetooth.*hci.*)(((un)?blocked)|((ge|ent)sperrt)) (blocked|gesperrt)")
re_bluetooth_pairable = re.compile(".*Pairable: yes")


def bluetooth_query_state():
    """


    Queries the current state of the Bluetooth unit.
    Returns:
        One of the following states:
        -255: could not determine Bluetooth state
        -3: bluetoothctl Error
        -2: Hardware-blocked Bluetooth Module
        -1: rfkill Error
        0: Bluetooth is disabled
        1: Bluetooth is enabled
        2: Bluetooth is in Pairing Mode
    """
    rfkill_output = subprocess.run(['rfkill'], stdout=subprocess.PIPE)  # run the "rfkill" command on a shell and save its output
    # now follows some tasty spaghetti code. Mmh yummy
    if rfkill_output.returncode != 0:
        return -1  # rfkill could not run successfully - something is seriously wrong
    if re_bluetooth_hwlock.match(rfkill_output.stdout.decode('utf-8')):
        return -2  # Bluetooth is HW-locked: can't reliably do anything about that
    if re_bluetooth_locked:
        return 0
    if re_bluetooth_unlocked:
        btctl_output = subprocess.run(['bluetoothctl show'], stdout=subprocess.PIPE)
        if rfkill_output.returncode != 0:
            return -3  # bluetoothctl could not run successfully - something is seriously wrong
        if re_bluetooth_pairable.match(btctl_output.stdout.decode('utf-8')):
            return 2  # we're pairable
        return 1  # not pairable, but unblocked

    return -255


def bluetooth_set_state(new_state: int):
    """


    Sets the desired Bluetooth state as specified in new_state.
    Valid stats are:
    0: Bluetooth is disabled
    1: Bluetooth is enabled
    2: Bluetooth is in Pairing Mode
    Returns:
        The new Bluetooth state using bluetooth_query_state()
    """
    old_state = bluetooth_query_state()
    if old_state == new_state:
        return new_state
    if new_state == 0:
        subprocess.run(['rfkill', 'block', 'bluetooth'])
    else:
        subprocess.run(['rfkill', 'unblock', 'bluetooth'])
        if new_state == 2:
            subprocess.run(['bluetoothctl', 'pairable', 'yes'])
        else:
            subprocess.run(['bluetoothctl', 'pairable', 'no'])


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
    return str(subprocess.run(["sudo shutdown", "-r" "t 5"]).returncode)


@app.route('/shutdown', methods=['GET'])
def system_shutdown():
    """

    Creates an API endpoint to shut down the backend Host.
    A simple GET request will trigger a shutdown after 5 seconds.
    Returns:
        The exit code of the shutdown command
"""
    return str(subprocess.run(["sudo shutdown", "-h", "t 5"]).returncode)


@app.route('/bluetooth', methods=['POST', 'GET'])
def bluetooth_status():
    """


    Creates an API endpoint to query and manipulate the Bluetooth Status.
    A simple GET request will return the current state.
    A POST request with the "state" form will set the Bluetooth state.
    Valid states are:
    0: Bluetooth is disabled
    1: Bluetooth is enabled
    2: Bluetooth is enabled and in Pairing mode
    Returns:
        The Bluetooth state as reported by the host
    """
    if request.method == "POST":
        state = int(request.form['state'])
        # input sanitizing
        if state > 2:
            state = 2
        if state < 0:
            state = 0
        bluetooth_set_state(state)
    return bluetooth_query_state()


@app.route('/disk', methods=['POST', 'GET'])
def disk_protection():
    """


    Creates an API endpoint to query and manipulate the disk protection status.
    A simple GET request will return the current state.
    A POST request with the "protection" form will enable (1) or disable (0) the write-protection of the mmcblk
    Returns:
        The write-protection state as reported by the host
    """
