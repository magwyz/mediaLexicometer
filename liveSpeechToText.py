#!/usr/bin/env python3

from vosk import Model, KaldiRecognizer, SetLogLevel
import os
import json
import subprocess
import threading
import multiprocessing
import argparse

sample_rate = 48000


def initRecognizer():
    SetLogLevel(0)
    model = Model("model")
    global rec
    rec = KaldiRecognizer(model, sample_rate)
    rec.SetWords(True)


def speechToText(data):
    global rec
    if rec.AcceptWaveform(data):
        jres = json.loads(rec.Result())
        print(jres['text'])


def processReadChannel(pool, program):
    bufferLenSec = 60
    audioData = b""
    toRead = sample_rate * bufferLenSec * 2

    fifoName = "fifo" + str(program)
    fd = open(fifoName, "rb")

    while True:
        data = fd.read(toRead)
        audioData += data
        if len(audioData) >= toRead:
            pool.apply_async(speechToText, (audioData,))
            audioData = b""


def process(adapterDrv, programs):
    pool = multiprocessing.Pool(len(programs), initRecognizer)

    adapterDrv = "/dev/dvb/adapter0/dvr0"

    ffmpegCmdLine = ['ffmpeg', '-y', '-i', adapterDrv]

    for p in programs:
        fifoName = "fifo" + str(p)
        try:
            os.mkfifo(fifoName)
        except FileExistsError:
            pass
        ffmpegCmdLine += ['-map', '0:p:%d:a:0' % p, '-ar', str(sample_rate) , '-ac', '1', '-f', 's16le', fifoName]

    subprocess.Popen(ffmpegCmdLine)

    threads = []
    for p in programs:
        t = threading.Thread(target = processReadChannel, args = (pool, p))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()


if __name__ == "__main__":
    if not os.path.exists("model"):
        print ("Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
        exit (1)

    parser = argparse.ArgumentParser(description = 'Capture programw from a DVB transponder and convert speech to text')
    parser.add_argument('programs', type=int, nargs='+',
        help = "the programs")
    parser.add_argument('--adapter-drv', default = "/dev/dvb/adapter0/dvr0",
        help = "Adapter driver")

    args = parser.parse_args()

    process(args.adapter_drv, args.programs)
