import logging
import os
import queue
import re
import sys
from collections import deque

import numpy as np
import serial
from scipy.signal import periodogram

from hotword import Hotword
from play import Player


logging.basicConfig()
logger = logging.getLogger("main")
logger.setLevel(logging.INFO)

def get_alpha_beta_ratio(sample):
    """Calculate Power Spectral Density.

    Args:
        sample (numpy.ndarray): EEG signal.

    Returns:
        float: ratio of alpha-band energy to beta-band energy.

    """
    freq, psd = periodogram(sample, SAMPLE_RATE)
    Ea = sum(psd[np.logical_and(freq>=8  , freq<=13)])
    Eb = sum(psd[np.logical_and(freq>=14 , freq<=30)])
    return Ea/Eb

# Initiate serial connection.
try:
    DEV_PATH = "/dev/"
    ports = [os.path.join(DEV_PATH, p) for p in os.listdir(DEV_PATH)
            if p.startswith("cu.usbmodem")]
    if not ports: # No available serial ports.
        raise serial.serialutil.SerialException
    ser = serial.Serial(ports[0], 9600, timeout=0.5)
    logger.info("Connected to port {}.".format(ports[0]))
except serial.serialutil.SerialException:
    logger.error("Failed to initiate serial connection.")
    sys.exit(1)

pos = 0
frame = np.zeros(100);
frame_for_process = np.zeros(100);
SAMPLE_RATE = 178 # Hz.

strikes = deque([False]*10, 10)
cb_queue = queue.Queue() # Callback queue for passing tasks between threads.
hw = Hotword(strikes, cb_queue)
player = Player()

input("Press enter to continue...")
try:
    ser.reset_input_buffer()
    while True:
        data = ser.readline().decode("utf-8")
        if not re.match(r"[-+]?\d+\s*$", data):
            continue

        # Update frame.
        frame[pos] = data
        pos = (pos + 1) % 100

        # Update frame_for_process.
        if pos != 0 and pos != 50:
            continue
        if pos == 0:
            frame_for_process[:50] = frame[:50]
            frame_for_process[50:] = frame[50:]
        elif pos == 50:
            frame_for_process[:50] = frame[50:]
            frame_for_process[50:] = frame[:50]

        ratio = get_alpha_beta_ratio(frame_for_process)
        logger.debug("Alpha-beta-ratio = {:.5f}".format(ratio))
        if ratio < 0.3:
            strikes.append(True)
        else:
            strikes.append(False)
        logger.info(strikes.count(False))

        if not cb_queue.empty():
            video, level = cb_queue.get(block=True)
            logger.info("Ready to play {} with level {}.".format(video, level))
            player.play(video, level)
            # Remove additional play tasks added during previous playing.
            with cb_queue.mutex:
                cb_queue.queue.clear()

except KeyboardInterrupt:
    player.destroy()
    hw.destroy()
    ser.close()
    logger.debug("Program Terminated.")
