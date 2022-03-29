#!/usr/bin/env python3

from vosk import Model, KaldiRecognizer, SetLogLevel
import os
import json
import subprocess
import threading
import multiprocessing
import argparse
import datetime
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mediaAnalysis.settings")

import django
django.setup()
from django.db import connection

import spacy


import database
from wordProcessing import addResultToDB

sample_rate = 48000


def initRecognizer(common_model, common_nlp):
    global rec
    rec = KaldiRecognizer(common_model, sample_rate)
    rec.SetWords(True)
    global nlp
    nlp = common_nlp


def speechToText(data, dateTime, channel):
    connection.close()
    global rec
    global nlp
    if rec.AcceptWaveform(data):
        jres = json.loads(rec.Result())
        try:
            addResultToDB(jres, dateTime, channel, nlp)
        except:
            import traceback
            traceback.print_exc()


def processReadChannel(pool, poolLock, channel):
    bufferLenSec = 60
    audioData = b""
    dateTime = datetime.datetime.now()
    toRead = sample_rate * bufferLenSec * 2

    fifoName = "fifo" + str(channel.programId)
    fd = open(fifoName, "rb")

    while True:
        data = fd.read(toRead)
        audioData += data
        if len(audioData) >= toRead:
            poolLock.acquire()
            pool.apply_async(speechToText, (audioData, dateTime, channel))
            poolLock.release()
            audioData = b""
            dateTime = datetime.datetime.now()


def process(adapterDrv, channels):
    SetLogLevel(0)
    model = Model("model")

    nlp = spacy.load("fr_core_news_sm-3.1.0")

    multiprocessing.set_start_method('fork')
    pool = multiprocessing.Pool(len(channels), initRecognizer, (model, nlp))

    ffmpegCmdLine = ['ffmpeg', '-y', '-v', 'quiet', '-i', adapterDrv]

    for channel in channels:
        p = channel.programId
        fifoName = "fifo" + str(p)
        try:
            os.mkfifo(fifoName)
        except FileExistsError:
            pass
        ffmpegCmdLine += ['-map', '0:p:%d:a:0' % p, '-ar', str(sample_rate) , '-ac', '1', '-f', 's16le', fifoName]

    subprocess.Popen(ffmpegCmdLine)

    threads = []
    poolLock = threading.Lock()
    for channel in channels:
        t = threading.Thread(target = processReadChannel, args = (pool, poolLock, channel))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()


if __name__ == "__main__":
    if not os.path.exists("model"):
        print ("Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
        exit (1)

    parser = argparse.ArgumentParser(description = 'Capture channels from a DVB transponder and convert speech to text')
    parser.add_argument('channels', nargs='+', help = "the channel names")
    parser.add_argument('--adapter-drv', default = "/dev/dvb/adapter0/dvr0",
        help = "Adapter driver")

    args = parser.parse_args()

    channels = database.getChannels(args.channels)

    process(args.adapter_drv, channels)
